plugins {
 id("com.android.application")
 id("org.jetbrains.kotlin.android")
 id("org.jetbrains.kotlin.plugin.compose")
 id("com.google.devtools.ksp")
}
android {
 namespace = "pk.karachibuses.app"
 compileSdk = 35
 defaultConfig {
  applicationId = "pk.karachibuses.app"
  minSdk = 26
  targetSdk = 35
  versionCode = 1
  versionName = "0.1.0"
  val mapStyleUrl = providers.gradleProperty("MAP_STYLE_URL").orElse("").get().replace("\\", "\\\\").replace("\"", "\\\"")
  val mapAttribution = providers.gradleProperty("MAP_ATTRIBUTION").orElse("").get().replace("\\", "\\\\").replace("\"", "\\\"")
  val mapSource = providers.gradleProperty("MAP_SOURCE_NAME").orElse("").get().replace("\\", "\\\\").replace("\"", "\\\"")
  val mapLicense = providers.gradleProperty("MAP_LICENSE_NAME").orElse("").get().replace("\\", "\\\\").replace("\"", "\\\"")
  val mapLicenseUrl = providers.gradleProperty("MAP_LICENSE_URL").orElse("").get().replace("\\", "\\\\").replace("\"", "\\\"")
  val offlineAllowed = providers.gradleProperty("MAP_OFFLINE_ALLOWED").orElse("false").get()
  buildConfigField("String", "MAP_STYLE_URL", "\"$mapStyleUrl\"")
  buildConfigField("String", "MAP_ATTRIBUTION", "\"$mapAttribution\"")
  buildConfigField("String", "MAP_SOURCE_NAME", "\"$mapSource\"")
  buildConfigField("String", "MAP_LICENSE_NAME", "\"$mapLicense\"")
  buildConfigField("String", "MAP_LICENSE_URL", "\"$mapLicenseUrl\"")
  buildConfigField("boolean", "MAP_OFFLINE_ALLOWED", offlineAllowed)
 }
 buildFeatures { compose = true; buildConfig = true }
 buildTypes {
  debug { applicationIdSuffix = ".debug"; buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:5000/api/v1/\"") }
  release { isMinifyEnabled = true; buildConfigField("String", "API_BASE_URL", "\"https://example.invalid/api/v1/\""); proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro") }
 }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
 kotlinOptions { jvmTarget = "17" }
}
dependencies {
 val bom = platform("androidx.compose:compose-bom:2024.12.01")
 implementation(bom); androidTestImplementation(bom)
 implementation("androidx.core:core-ktx:1.15.0")
 implementation("androidx.activity:activity-compose:1.9.3")
 implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
 implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
 implementation("androidx.compose.ui:ui"); implementation("androidx.compose.ui:ui-tooling-preview"); implementation("androidx.compose.material3:material3")
 debugImplementation("androidx.compose.ui:ui-tooling")
 implementation("androidx.room:room-runtime:2.6.1"); implementation("androidx.room:room-ktx:2.6.1"); ksp("androidx.room:room-compiler:2.6.1")
 implementation("com.squareup.retrofit2:retrofit:2.11.0"); implementation("com.squareup.retrofit2:converter-gson:2.11.0"); implementation("com.squareup.okhttp3:okhttp:4.12.0")
 implementation("org.maplibre.gl:android-sdk:13.6.1")
 implementation("androidx.work:work-runtime-ktx:2.10.0"); implementation("androidx.datastore:datastore-preferences:1.1.1")
 testImplementation("junit:junit:4.13.2"); androidTestImplementation("androidx.test.ext:junit:1.2.1")
}