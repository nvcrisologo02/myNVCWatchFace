// NVC Orbita: fourth resource-only Watch Face Format package (design 2026-11-26-orbita-design.md).
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.nvc.orbita"
    compileSdk = 37
    compileSdkMinor = 1

    defaultConfig {
        applicationId = "com.nvc.orbita"
        // WFF v2 requires Wear OS 5 / API 34 (developer.android.com/training/wearables/wff, "Versioning in WFF").
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
        }
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
