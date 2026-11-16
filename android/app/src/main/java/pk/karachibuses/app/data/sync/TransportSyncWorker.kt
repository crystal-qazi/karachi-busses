package pk.karachibuses.app.data.sync
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import pk.karachibuses.app.data.AppContainer
import java.util.concurrent.TimeUnit

class TransportSyncWorker(context:Context,params:WorkerParameters):CoroutineWorker(context,params){
 override suspend fun doWork():Result = withContext(Dispatchers.IO){
  runCatching { AppContainer(applicationContext).repository.sync().getOrThrow() }
   .fold({Result.success()},{Result.retry()})
 }
 companion object {
  fun schedule(context:Context){
   val constraints=Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
   val request=PeriodicWorkRequestBuilder<TransportSyncWorker>(12,TimeUnit.HOURS)
    .setConstraints(constraints).setBackoffCriteria(BackoffPolicy.EXPONENTIAL,30,TimeUnit.SECONDS).build()
   WorkManager.getInstance(context).enqueueUniquePeriodicWork("published-transport-sync",ExistingPeriodicWorkPolicy.KEEP,request)
  }
 }
}