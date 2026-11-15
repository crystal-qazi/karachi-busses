package pk.karachibuses.app.data
import androidx.room.withTransaction
import kotlinx.coroutines.flow.Flow
import pk.karachibuses.app.data.local.*
import pk.karachibuses.app.data.remote.MobileApi
import pk.karachibuses.app.data.remote.DatasetChecksum
import pk.karachibuses.app.domain.JourneyPlanner
import pk.karachibuses.app.domain.JourneyOption
import pk.karachibuses.app.data.local.StopEntity
class TransportRepository(private val api:MobileApi,private val db:TransportDatabase){
 val routes:Flow<List<RouteEntity>> = db.dao().observeRoutes()
 fun search(q:String):Flow<List<RouteEntity>> = db.dao().searchRoutes(q)
 suspend fun nearbyStops(lat:Double,lng:Double,radius:Double=1500.0):List<Pair<StopEntity,Double>> = db.dao().allStops().map { it to haversine(lat,lng,it.latitude,it.longitude) }.filter { it.second<=radius }.sortedBy { it.second }
 suspend fun planJourney(lat:Double,lng:Double,destination:String,radius:Double=1500.0):List<JourneyOption> = JourneyPlanner.plan(lat,lng,destination,radius,db.dao().allRoutes(),db.dao().allDirections(),db.dao().allStops(),db.dao().allDirectionStops())
 private fun haversine(a:Double,b:Double,c:Double,d:Double):Double { val p=Math.toRadians(c-a); val q=Math.toRadians(d-b); val x=kotlin.math.sin(p/2)*kotlin.math.sin(p/2)+kotlin.math.cos(Math.toRadians(a))*kotlin.math.cos(Math.toRadians(c))*kotlin.math.sin(q/2)*kotlin.math.sin(q/2); return 12742000.0*kotlin.math.asin(kotlin.math.sqrt(x.coerceIn(0.0,1.0))) }
 suspend fun sync():Result<Int> = runCatching {
  val response=api.snapshot()
  check(response.success && response.data!=null){response.error?.message ?: "Snapshot request failed"}
  val dto=response.data
  check(dto.schema_version==1){"Unsupported dataset schema"}
  val calculated=DatasetChecksum.sha256(dto.dataset)
  check(dto.dataset_version==calculated && dto.checksum=="sha256:"+calculated){"Snapshot checksum validation failed"}
  val dao=db.dao()
  db.withTransaction {
   dao.clearShapes();dao.clearDirectionStops();dao.clearDirections();dao.clearStops();dao.clearRoutes()
   dao.putRoutes(dto.dataset.routes.map{RouteEntity(it.id,it.route_code,it.route_name,it.description,it.operator_name)})
   dao.putDirections(dto.dataset.directions.map{DirectionEntity(it.id,it.route_id,it.direction_name,it.start_label,it.end_label)})
   dao.putStops(dto.dataset.stops.map{StopEntity(it.id,it.stop_name,it.latitude,it.longitude,it.address)})
   dao.putDirectionStops(dto.dataset.direction_stops.map{DirectionStopEntity(it.direction_id,it.stop_id,it.stop_sequence)})
   dao.putShapes(dto.dataset.shapes.map{RouteShapeEntity(it.direction_id,it.geojson.toString())})
   dao.putSyncState(SyncStateEntity(datasetVersion=dto.dataset_version,checksum=dto.checksum,syncedAt=System.currentTimeMillis()))
  }
  dto.dataset.routes.size
 }
}