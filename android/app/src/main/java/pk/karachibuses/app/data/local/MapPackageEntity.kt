package pk.karachibuses.app.data.local

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import kotlinx.coroutines.flow.Flow
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

/**
 * Local catalogue for independently versioned basemap packages.
 * A package is usable only after its archive has been verified and installed.
 */
@Entity(tableName = "map_packages", indices = [Index("kind"), Index("state")])
data class MapPackageEntity(
    @PrimaryKey val packageId: String,
    val displayName: String,
    /** "karachi_full" or "area". */
    val kind: String,
    val areaSlug: String?,
    val west: Double,
    val south: Double,
    val east: Double,
    val north: Double,
    val minZoom: Int,
    val maxZoom: Int,
    val packageVersion: String,
    val format: String,
    val sizeBytes: Long,
    val checksumSha256: String,
    val attribution: String,
    val sourceName: String,
    val licenceName: String,
    val licenceUrl: String?,
    val offlineDownloadAllowed: Boolean,
    val downloadUri: String?,
    /** queued, downloading, verifying, installed, failed, or update_available */
    val state: String,
    val installedPath: String?,
    val updatedAtEpochMs: Long
)

@Dao
interface MapPackageDao {
    @Query("SELECT * FROM map_packages ORDER BY kind, displayName")
    fun observePackages(): Flow<List<MapPackageEntity>>

    @Query("SELECT * FROM map_packages WHERE packageId = :packageId LIMIT 1")
    suspend fun findPackage(packageId: String): MapPackageEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun savePackage(package: MapPackageEntity)

    @Query("UPDATE map_packages SET state = :state WHERE packageId = :packageId")
    suspend fun updateState(packageId: String, state: String)

    @Query("UPDATE map_packages SET state = 'installed', installedPath = :path WHERE packageId = :packageId")
    suspend fun markInstalled(packageId: String, path: String)

    @Query("DELETE FROM map_packages WHERE packageId = :packageId")
    suspend fun removePackage(packageId: String)
}
