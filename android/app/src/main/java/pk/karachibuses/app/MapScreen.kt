package pk.karachibuses.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import kotlinx.coroutines.launch
import org.maplibre.android.MapLibre
import org.maplibre.android.camera.CameraPosition
import org.maplibre.android.geometry.LatLng
import org.maplibre.android.maps.MapLibreMap
import org.maplibre.android.maps.MapView
import org.maplibre.android.offline.OfflineManager
import org.maplibre.android.offline.OfflineRegion
import org.maplibre.android.offline.OfflineRegionError
import org.maplibre.android.offline.OfflineRegionStatus
import org.maplibre.android.offline.OfflineTilePyramidRegionDefinition
import pk.karachibuses.app.data.AppContainer
import pk.karachibuses.app.data.local.MapPackageEntity
import org.json.JSONObject

private const val MAX_AREA_DEGREES = 0.20
private const val AREA_MIN_ZOOM = 10.0
private const val AREA_MAX_ZOOM = 15.0

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MapScreen(container: AppContainer, onBack: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    val styleUrl = BuildConfig.MAP_STYLE_URL
    var map by remember { mutableStateOf<MapLibreMap?>(null) }
    var message by remember { mutableStateOf(
        if (styleUrl.isBlank()) "Map style is not configured. Set MAP_STYLE_URL in android/gradle.properties."
        else "Online map ready. Pan and zoom to a neighbourhood, then download the visible area."
    ) }
    var progress by remember { mutableStateOf<Float?>(null) }
    var mapView by remember { mutableStateOf<MapView?>(null) }
    val packages by container.database.mapPackageDao().observePackages().collectAsState(initial = emptyList())

    MapLibre.getInstance(context)

    DisposableEffect(lifecycleOwner, mapView) {
        val view = mapView
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_START -> view?.onStart()
                Lifecycle.Event.ON_RESUME -> view?.onResume()
                Lifecycle.Event.ON_PAUSE -> view?.onPause()
                Lifecycle.Event.ON_STOP -> view?.onStop()
                                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            view?.onDestroy()
        }
    }

    fun downloadVisibleArea() {
        val activeMap = map ?: run { message = "Wait for the map to finish loading."; return }
        if (styleUrl.isBlank()) { message = "Configure a map style URL before downloading."; return }
        if (!BuildConfig.MAP_OFFLINE_ALLOWED) {
            message = "Offline downloads are disabled until the configured map provider explicitly permits offline use."
            return
        }
        if (BuildConfig.MAP_ATTRIBUTION.isBlank() || BuildConfig.MAP_SOURCE_NAME.isBlank() ||
            BuildConfig.MAP_LICENSE_NAME.isBlank()) {
            message = "Offline downloads require MAP_ATTRIBUTION, MAP_SOURCE_NAME and MAP_LICENSE_NAME."
            return
        }

        val bounds = activeMap.projection.visibleRegion.latLngBounds
        val width = bounds.longitudeEast - bounds.longitudeWest
        val height = bounds.latitudeNorth - bounds.latitudeSouth
        if (width <= 0 || height <= 0 || width > MAX_AREA_DEGREES || height > MAX_AREA_DEGREES) {
            message = "Zoom in to a neighbourhood-sized area before downloading. Large city-wide downloads need a separately prepared package."
            return
        }

        progress = 0f
        message = "Preparing offline area…"
        val definition = OfflineTilePyramidRegionDefinition(
            styleUrl, bounds, AREA_MIN_ZOOM, AREA_MAX_ZOOM,
            context.resources.displayMetrics.density, false
        )
        val metadata = JSONObject()
            .put("name", "Karachi neighbourhood")
            .put("kind", "area")
            .put("createdAt", System.currentTimeMillis())
            .toString().toByteArray()

        OfflineManager.getInstance(context).createOfflineRegion(
            definition, metadata,
            object : OfflineManager.CreateOfflineRegionCallback {
                override fun onCreate(region: OfflineRegion) {
                    val packageId = "maplibre-area-${region.id}"
                    val entity = MapPackageEntity(
                        packageId = packageId,
                        displayName = "Downloaded neighbourhood",
                        kind = "area",
                        areaSlug = null,
                        west = bounds.longitudeWest,
                        south = bounds.latitudeSouth,
                        east = bounds.longitudeEast,
                        north = bounds.latitudeNorth,
                        minZoom = AREA_MIN_ZOOM.toInt(),
                        maxZoom = AREA_MAX_ZOOM.toInt(),
                        packageVersion = "local-${System.currentTimeMillis()}",
                        format = "maplibre-offline-region",
                        sizeBytes = 0L,
                        checksumSha256 = "",
                        attribution = BuildConfig.MAP_ATTRIBUTION,
                        sourceName = BuildConfig.MAP_SOURCE_NAME,
                        licenceName = BuildConfig.MAP_LICENSE_NAME,
                        licenceUrl = BuildConfig.MAP_LICENSE_URL.ifBlank { null },
                        offlineDownloadAllowed = true,
                        downloadUri = null,
                        state = "downloading",
                        installedPath = "maplibre-offline:${region.id}",
                        updatedAtEpochMs = System.currentTimeMillis()
                    )
                    scope.launch { container.database.mapPackageDao().savePackage(entity) }
                    region.setObserver(object : OfflineRegion.OfflineRegionObserver {
                        override fun onStatusChanged(status: OfflineRegionStatus) {
                            val required = status.requiredResourceCount
                            progress = if (required > 0) {
                                (status.completedResourceCount.toFloat() / required.toFloat()).coerceIn(0f, 1f)
                            } else null
                            if (status.isComplete) {
                                scope.launch {
                                    container.database.mapPackageDao().savePackage(
                                        entity.copy(
                                            sizeBytes = status.completedResourceSize,
                                            state = "installed",
                                            updatedAtEpochMs = System.currentTimeMillis()
                                        )
                                    )
                                }
                                message = "Offline neighbourhood saved (${status.completedTileCount} map tiles)."
                                progress = 1f
                            } else {
                                message = "Downloading map resources: ${status.completedResourceCount} / ${status.requiredResourceCount}"
                            }
                        }
                        override fun onError(error: OfflineRegionError) {
                            message = "Map download error: ${error.message}"
                            scope.launch { container.database.mapPackageDao().updateState(packageId, "failed") }
                        }
                        override fun mapboxTileCountLimitExceeded(limit: Long) {
                            message = "The map provider's offline tile limit was reached ($limit)."
                            scope.launch { container.database.mapPackageDao().updateState(packageId, "failed") }
                        }
                    })
                    region.setDownloadState(OfflineRegion.STATE_ACTIVE)
                }
                override fun onError(error: String) {
                    progress = null
                    message = "Could not create offline map area: $error"
                }
            }
        )
    }

    Scaffold(topBar = {
        TopAppBar(title = { Text("Karachi map") }, navigationIcon = {
            OutlinedButton(onClick = onBack) { Text("Back") }
        })
    }) { padding ->
        Column(
            Modifier.fillMaxSize().padding(padding).padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            AndroidView(
                modifier = Modifier.fillMaxWidth().weight(1f),
                factory = { viewContext ->
                    MapView(viewContext).also { view ->
                        view.onCreate(null)
                        mapView = view
                        view.getMapAsync { readyMap ->
                            map = readyMap
                            readyMap.uiSettings.isAttributionEnabled = true
                            readyMap.cameraPosition = CameraPosition.Builder()
                                .target(LatLng(24.8607, 67.0011))
                                .zoom(10.0)
                                .build()
                            if (styleUrl.isNotBlank()) {
                                readyMap.setStyle(styleUrl) {
                                    message = "Map loaded. Zoom into a neighbourhood to download it for offline use."
                                }
                            }
                        }
                    }
                }
            )
            Text(message, style = MaterialTheme.typography.bodySmall)
            if (BuildConfig.MAP_ATTRIBUTION.isNotBlank()) Text(BuildConfig.MAP_ATTRIBUTION, style = MaterialTheme.typography.labelSmall)
            progress?.let { LinearProgressIndicator(progress = it, modifier = Modifier.fillMaxWidth()) }
            Button(
                onClick = { downloadVisibleArea() },
                enabled = map != null && styleUrl.isNotBlank() && BuildConfig.MAP_OFFLINE_ALLOWED,
                modifier = Modifier.fillMaxWidth()
            ) { Text("Download visible neighbourhood") }

            packages.forEach { item ->
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("${item.displayName} • ${item.state} • ${item.sizeBytes / (1024 * 1024)} MB", style = MaterialTheme.typography.bodySmall)
                    androidx.compose.foundation.layout.Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (item.state == "downloading" || item.state == "paused") {
                            OutlinedButton(onClick = {
                                val id = item.packageId.substringAfterLast("-").toLongOrNull()
                                if (id != null) OfflineManager.getInstance(context).getOfflineRegion(id,
                                    object : OfflineManager.GetOfflineRegionCallback {
                                        override fun onRegion(region: OfflineRegion) {
                                            val next = if (item.state == "downloading") OfflineRegion.STATE_INACTIVE else OfflineRegion.STATE_ACTIVE
                                            region.setDownloadState(next)
                                            val state = if (next == OfflineRegion.STATE_ACTIVE) "downloading" else "paused"
                                            scope.launch { container.database.mapPackageDao().updateState(item.packageId, state) }
                                            message = if (state == "paused") "Offline map download paused." else "Offline map download resumed."
                                        }
                                        override fun onRegionNotFound() { message = "Offline region no longer exists in MapLibre storage." }
                                        override fun onError(error: String) { message = error }
                                    })
                            }) { Text(if (item.state == "downloading") "Pause" else "Resume") }
                        }
                        OutlinedButton(onClick = {
                            val id = item.packageId.substringAfterLast("-").toLongOrNull()
                            if (id != null) OfflineManager.getInstance(context).getOfflineRegion(id,
                                object : OfflineManager.GetOfflineRegionCallback {
                                    override fun onRegion(region: OfflineRegion) {
                                        region.delete(object : OfflineRegion.OfflineRegionDeleteCallback {
                                            override fun onDelete() {
                                                scope.launch { container.database.mapPackageDao().removePackage(item.packageId) }
                                                message = "Offline map removed."
                                            }
                                            override fun onError(error: String) { message = "Could not remove map: $error" }
                                        })
                                    }
                                    override fun onRegionNotFound() {
                                        scope.launch { container.database.mapPackageDao().removePackage(item.packageId) }
                                    }
                                    override fun onError(error: String) { message = error }
                                })
                        }) { Text("Remove") }
                    }
                }
            }
            Text(
                "Transport routes and stops remain available from the offline database. A full Karachi basemap requires a reviewed city boundary and a separately tested package; this screen deliberately limits interactive downloads to neighbourhood-sized regions.",
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
