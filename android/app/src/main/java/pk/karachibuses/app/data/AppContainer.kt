package pk.karachibuses.app.data
import android.content.Context
import androidx.room.Room
import pk.karachibuses.app.BuildConfig
import pk.karachibuses.app.data.local.TransportDatabase
import pk.karachibuses.app.data.remote.MobileApi
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
class AppContainer(context:Context){
 val database=Room.databaseBuilder(context,TransportDatabase::class.java,"karachi-buses.db").build()
 private val api=Retrofit.Builder().baseUrl(BuildConfig.API_BASE_URL).addConverterFactory(GsonConverterFactory.create()).build().create(MobileApi::class.java)
 val repository=TransportRepository(api,database)
}