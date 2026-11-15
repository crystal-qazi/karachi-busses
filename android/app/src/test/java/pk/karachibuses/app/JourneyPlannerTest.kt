package pk.karachibuses.app
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import pk.karachibuses.app.data.local.*
import pk.karachibuses.app.domain.JourneyPlanner

class JourneyPlannerTest {
 @Test fun findsOneTransferJourneyFromLocalRecords() {
  val routes=listOf(RouteEntity(1,"R1","Route 1",null,null),RouteEntity(2,"R2","Route 2",null,null))
  val directions=listOf(DirectionEntity(10,1,"Outbound",null,null),DirectionEntity(20,2,"Outbound",null,null))
  val stops=listOf(StopEntity(1,"Origin",24.8607,67.0011,null),StopEntity(2,"Transfer",24.861,67.002,null),StopEntity(3,"Destination",24.862,67.003,null))
  val links=listOf(DirectionStopEntity(10,1,1),DirectionStopEntity(10,2,2),DirectionStopEntity(20,2,1),DirectionStopEntity(20,3,2))
  val result=JourneyPlanner.plan(24.8607,67.0011,"Destination",1000.0,routes,directions,stops,links)
  assertEquals(1,result.size)
  assertEquals(listOf("R1","R2"),result.first().routeCodes)
  assertEquals("Transfer",result.first().transferStop)
 }
 @Test fun rejectsDestinationBeforeBoardingStop() {
  val routes=listOf(RouteEntity(1,"R1","Route 1",null,null))
  val directions=listOf(DirectionEntity(10,1,"Outbound",null,null))
  val stops=listOf(StopEntity(1,"Origin",24.8607,67.0011,null),StopEntity(2,"Destination",24.862,67.003,null))
  val links=listOf(DirectionStopEntity(10,2,1),DirectionStopEntity(10,1,2))
  val result=JourneyPlanner.plan(24.8607,67.0011,"Destination",1000.0,routes,directions,stops,links)
  assertTrue(result.isEmpty())
 }
}