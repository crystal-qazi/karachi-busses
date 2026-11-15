package pk.karachibuses.app.ui
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import pk.karachibuses.app.data.TransportRepository
import pk.karachibuses.app.domain.JourneyOption
import pk.karachibuses.app.data.local.StopEntity
class HomeViewModel(private val repository:TransportRepository):ViewModel(){
 private val query=MutableStateFlow("")
 val routes=query.flatMapLatest{if(it.isBlank()) repository.routes else repository.search(it)}.stateIn(viewModelScope,SharingStarted.WhileSubscribed(5000),emptyList())
 private val _nearby=MutableStateFlow<List<Pair<StopEntity,Double>>>(emptyList())
 val nearby:StateFlow<List<Pair<StopEntity,Double>>> = _nearby
 private val _journeys=MutableStateFlow<List<JourneyOption>>(emptyList())
 val journeys:StateFlow<List<JourneyOption>> = _journeys
 private val _status=MutableStateFlow("Offline-ready • synchronize to download published routes")
 val status:StateFlow<String> = _status
 fun search(value:String){query.value=value}
 fun clearSearch(){query.value=""}
 fun findNearby(lat:String,lng:String){viewModelScope.launch{val a=lat.toDoubleOrNull();val b=lng.toDoubleOrNull();if(a==null||b==null){_status.value="Enter valid origin coordinates";return@launch};runCatching{repository.nearbyStops(a,b)}.onSuccess{_nearby.value=it;_status.value="Found "+it.size+" nearby stops in the offline database"}.onFailure{_status.value="Nearby search failed: "+(it.message ?: "unknown error")}}}
 fun plan(lat:String,lng:String,destination:String){viewModelScope.launch{val a=lat.toDoubleOrNull();val b=lng.toDoubleOrNull();if(a==null||b==null||destination.isBlank()){_status.value="Enter valid origin coordinates and a destination stop name";_journeys.value=emptyList();return@launch};runCatching{repository.planJourney(a,b,destination)}.onSuccess{_journeys.value=it;_status.value="Found "+it.size+" offline journey options"}.onFailure{_status.value="Journey search failed: "+(it.message ?: "unknown error")}}}
 fun sync(){viewModelScope.launch{_status.value="Synchronizing…";repository.sync().onSuccess{_status.value="Synced "+it+" routes • saved for offline use"}.onFailure{_status.value="Sync failed • saved data remains available ("+(it.message ?: "network error")+")"}}}
}