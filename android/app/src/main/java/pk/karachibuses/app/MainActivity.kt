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
class MainActivity:ComponentActivity(){
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);val container=AppContainer(applicationContext);setContent{MaterialTheme{HomeScreen(container)}}}
}
@OptIn(ExperimentalMaterial3Api::class)
@Composable private fun HomeScreen(container:AppContainer){
 val vm= remember{HomeViewModel(container.repository)}
 val routes by vm.routes.collectAsStateWithLifecycle()
 val status by vm.status.collectAsStateWithLifecycle()
 var query by remember{mutableStateOf("")}
 Scaffold(topBar={TopAppBar(title={Text("Karachi Buses")})}){padding->
  Column(Modifier.fillMaxSize().padding(padding).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
   Text("Discover public transport across Karachi",style=MaterialTheme.typography.titleMedium)
   Text(status,style=MaterialTheme.typography.bodySmall)
   OutlinedTextField(query,{query=it;vm.search(it)},Modifier.fillMaxWidth(),label={Text("Search routes")},singleLine=true)
   Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){
    Button(onClick=vm::sync){Text("Sync now")}
    OutlinedButton(onClick={query="";vm.clearSearch()}){Text("Clear")}
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