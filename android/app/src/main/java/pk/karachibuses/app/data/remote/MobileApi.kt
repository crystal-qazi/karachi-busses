package pk.karachibuses.app.data.remote
import retrofit2.http.GET
data class ApiEnvelope<T>(val success:Boolean,val data:T?,val error:ApiError?)
data class ApiError(val code:String,val message:String)
data class SnapshotDto(val dataset_version:String,val schema_version:Int,val checksum:String,val generated_at:String,val dataset:DatasetDto)
data class DatasetDto(val routes:List<RouteDto>,val directions:List<DirectionDto>,val stops:List<StopDto>,val direction_stops:List<DirectionStopDto>,val shapes:List<ShapeDto>)
data class RouteDto(val id:Long,val route_code:String,val route_name:String,val description:String?,val operator_name:String?)
data class DirectionDto(val id:Long,val route_id:Long,val direction_name:String,val start_label:String?,val end_label:String?)
data class StopDto(val id:Long,val stop_name:String,val latitude:Double,val longitude:Double,val address:String?)
data class DirectionStopDto(val direction_id:Long,val stop_id:Long,val stop_sequence:Int)
data class ShapeDto(val direction_id:Long,val geojson:Any?)
interface MobileApi { @GET("mobile/snapshot") suspend fun snapshot():ApiEnvelope<SnapshotDto> }