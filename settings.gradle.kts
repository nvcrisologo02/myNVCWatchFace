pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "myNVCWatchFace"
include(":watchface")
// Debug-only test provider: fake glucose complications to force states Gluroo cannot (plan, task 6).
include(":fakeglucose")
// Second watch face (design docs/superpowers/specs/2026-11-23-navigator-design.md).
include(":navigator")
