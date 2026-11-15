package pk.karachibuses.app.ui
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import pk.karachibuses.app.data.TransportRepository
class HomeViewModel(private val repository:TransportRepository):ViewModel(){
 private val query=MutableStateFlow("")
 val routes=query.flatMapLatest{if(it.isBlank()) repository.routes else repository.search(it)}.stateIn(viewModelScope,SharingStarted.WhileSubscribed(5000),emptyList())
 private val _status=MutableStateFlow("Offline-ready • synchronize to download published routes")
 val status:StateFlow<String> = _status
 fun search(value:String){query.value=value}
 fun clearSearch(){query.value=""}
 fun sync(){viewModelScope.launch{_status.value="Synchronizing…";repository.sync().onSuccess{_status.value="Synced "+it+" routes • saved for offline use"}.onFailure{_status.value="Sync failed • saved data remains available ("+(it.message ?: "network error")+")"}}}
}