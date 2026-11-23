@echo off
rem Builds with Android Studio's JBR. Default task: the debug watch face APK.
rem   scripts\build.bat                          -> :watchface:assembleDebug
rem   scripts\build.bat :fakeglucose:assembleDebug
set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
set "ROOT=C:\Users\criso\source\repos\myNVCWatchFace"
set "TASK=%~1"
if "%TASK%"=="" set "TASK=:watchface:assembleDebug"
cd /d "%ROOT%"
call "%ROOT%\gradlew.bat" -p "%ROOT%" %TASK% --console=plain -q
exit /b %ERRORLEVEL%
