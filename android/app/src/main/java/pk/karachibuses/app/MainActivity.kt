package pk.karachibuses.app
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pk.karachibuses.app.data.AppContainer
import pk.karachibuses.app.data.local.RouteEntity
import pk.karachibuses.app.ui.HomeViewModel
import pk.karachibuses.app.data.sync.TransportSyncWorker
class MainActivity:ComponentActivity(){
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);val container=AppContainer(applicationContext);TransportSyncWorker.schedule(applicationContext);setContent{MaterialTheme{HomeScreen(container)}}}
}
@OptIn(ExperimentalMaterial3Api::class)
@Composable private fun HomeScreen(container:AppContainer){
 val vm= remember{HomeViewModel(container.repository)}
 val routes by vm.routes.collectAsStateWithLifecycle()
 val status by vm.status.collectAsStateWithLifecycle()
 val journeys by vm.journeys.collectAsStateWithLifecycle()
 val nearby by vm.nearby.collectAsStateWithLifecycle()
 var query by remember{mutableStateOf("")}
 var originLat by remember{mutableStateOf("24.8607")}
 var originLng by remember{mutableStateOf("67.0011")}
 var destination by remember{mutableStateOf("")}
 Scaffold(topBar={TopAppBar(title={Text("Karachi Buses")})}){padding->
  Column(Modifier.fillMaxSize().padding(padding).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
   Text("Discover public transport across Karachi",style=MaterialTheme.typography.titleMedium)
   Text(status,style=MaterialTheme.typography.bodySmall)
   OutlinedTextField(query,{query=it;vm.search(it)},Modifier.fillMaxWidth(),label={Text("Search routes")},singleLine=true)
   Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){
    Button(onClick=vm::sync){Text("Sync now")}
    OutlinedButton(onClick={query="";vm.clearSearch()}){Text("Clear")}
   }
   Text("Offline journey planner",style=MaterialTheme.typography.titleLarge)
   Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
    OutlinedTextField(originLat,{originLat=it},Modifier.weight(1f),label={Text("Origin latitude")},singleLine=true)
    OutlinedTextField(originLng,{originLng=it},Modifier.weight(1f),label={Text("Origin longitude")},singleLine=true)
   }
   OutlinedButton(onClick={vm.findNearby(originLat,originLng)}){Text("Find nearby stops offline")}
   nearby.forEach { (stop,distance) -> Text(stop.stopName+" • "+distance.toInt()+" m") }
   OutlinedTextField(destination,{destination=it},Modifier.fillMaxWidth(),label={Text("Destination stop name")},singleLine=true)
   OutlinedButton(onClick={vm.plan(originLat,originLng,destination)}){Text("Find offline journey")}
   journeys.forEach { option ->
    ElevatedCard(Modifier.fillMaxWidth()) { Column(Modifier.padding(12.dp)) {
     Text(option.routeCodes.joinToString(" → "),style=MaterialTheme.typography.titleMedium)
     Text("Board: "+option.boardingStop)
     option.transferStop?.let { Text("Transfer: "+it) }
     Text("Destination: "+option.destinationStop)
    } }
   }
   Text("Routes saved on this device",style=MaterialTheme.typography.titleLarge)
   if(routes.isEmpty()) Text("No routes downloaded yet. Connect to the server and synchronize.")
   LazyColumn(verticalArrangement=Arrangement.spacedBy(8.dp)){items(routes){RouteRow(it)}}
  }
 }
}
@Composable private fun RouteRow(route:RouteEntity){
 ElevatedCard(Modifier.fillMaxWidth()){Column(Modifier.padding(12.dp)){
  Text(route.routeCode,style=MaterialTheme.typography.titleMedium)
  Text(route.routeName)
  route.operatorName?.let{Text(it,style=MaterialTheme.typography.bodySmall)}
 }}
}