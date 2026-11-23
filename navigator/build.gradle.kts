// NVC Navigator: second resource-only Watch Face Format package (design 2026-11-23-navigator-design.md).
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.nvc.navigator"
    compileSdk = 37
    compileSdkMinor = 1

    defaultConfig {
        applicationId = "com.nvc.navigator"
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
