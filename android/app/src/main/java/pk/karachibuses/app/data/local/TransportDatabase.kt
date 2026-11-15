package pk.karachibuses.app.data.local
import androidx.room.*
import kotlinx.coroutines.flow.Flow
@Entity(tableName="routes", indices=[Index(value=["routeCode"], unique=true)])
data class RouteEntity(@PrimaryKey val id:Long,val routeCode:String,val routeName:String,val description:String?,val operatorName:String?)
@Entity(tableName="directions", indices=[Index("routeId")])
data class DirectionEntity(@PrimaryKey val id:Long,val routeId:Long,val directionName:String,val startLabel:String?,val endLabel:String?)
@Entity(tableName="stops", indices=[Index("stopName")])
data class StopEntity(@PrimaryKey val id:Long,val stopName:String,val latitude:Double,val longitude:Double,val address:String?)
@Entity(tableName="direction_stops",primaryKeys=["directionId","stopId"],indices=[Index(value=["directionId","sequence"],unique=true),Index("stopId")])
data class DirectionStopEntity(val directionId:Long,val stopId:Long,val sequence:Int)
@Entity(tableName="route_shapes")
data class RouteShapeEntity(@PrimaryKey val directionId:Long,val geoJson:String)
@Entity(tableName="sync_state")
data class SyncStateEntity(@PrimaryKey val id:Int=1,val datasetVersion:String,val checksum:String,val syncedAt:Long)
@Dao interface TransportDao {
 @Query("SELECT * FROM routes ORDER BY routeCode") fun observeRoutes():Flow<List<RouteEntity>>
 @Query("SELECT * FROM routes") suspend fun allRoutes():List<RouteEntity>
 @Query("SELECT * FROM directions") suspend fun allDirections():List<DirectionEntity>
 @Query("SELECT * FROM stops") suspend fun allStops():List<StopEntity>
 @Query("SELECT * FROM direction_stops ORDER BY directionId, sequence") suspend fun allDirectionStops():List<DirectionStopEntity>
 @Query("SELECT * FROM routes WHERE routeCode LIKE '%' || :q || '%' OR routeName LIKE '%' || :q || '%' ORDER BY routeCode") fun searchRoutes(q:String):Flow<List<RouteEntity>>
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putRoutes(v:List<RouteEntity>)
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putDirections(v:List<DirectionEntity>)
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putStops(v:List<StopEntity>)
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putDirectionStops(v:List<DirectionStopEntity>)
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putShapes(v:List<RouteShapeEntity>)
 @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun putSyncState(v:SyncStateEntity)
 @Query("DELETE FROM route_shapes") suspend fun clearShapes()
 @Query("DELETE FROM direction_stops") suspend fun clearDirectionStops()
 @Query("DELETE FROM directions") suspend fun clearDirections()
 @Query("DELETE FROM stops") suspend fun clearStops()
 @Query("DELETE FROM routes") suspend fun clearRoutes()
}
@Database(entities=[RouteEntity::class,DirectionEntity::class,StopEntity::class,DirectionStopEntity::class,RouteShapeEntity::class,SyncStateEntity::class],version=1,exportSchema=true)
abstract class TransportDatabase:RoomDatabase(){ abstract fun dao():TransportDao }