package pk.karachibuses.app.data
import androidx.room.withTransaction
import kotlinx.coroutines.flow.Flow
import pk.karachibuses.app.data.local.*
import pk.karachibuses.app.data.remote.MobileApi
class TransportRepository(private val api:MobileApi,private val db:TransportDatabase){
 val routes:Flow<List<RouteEntity>> = db.dao().observeRoutes()
 fun search(q:String):Flow<List<RouteEntity>> = db.dao().searchRoutes(q)
 suspend fun sync():Result<Int> = runCatching {
  val response=api.snapshot()
  check(response.success && response.data!=null){response.error?.message ?: "Snapshot request failed"}
  val dto=response.data
  check(dto.schema_version==1){"Unsupported dataset schema"}
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