// Test tool only: publishes fake glucose complications so every glucose state of the watch face
// can be forced from adb. Never part of the watch face. Written in Java because the project
// disables the default Kotlin stdlib (the watch face package must not contain code).
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.nvc.fakeglucose"
    compileSdk = 37
    compileSdkMinor = 1

    defaultConfig {
        applicationId = "com.nvc.fakeglucose"
        minSdk = 30
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation(libs.androidx.complications.data.source)
}
