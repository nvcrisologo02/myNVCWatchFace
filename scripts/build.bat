@echo off
rem Builds the debug watch face APK with Android Studio's JBR.
set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
set "ROOT=C:\Users\criso\source\repos\myNVCWatchFace"
cd /d "%ROOT%"
call "%ROOT%\gradlew.bat" -p "%ROOT%" :watchface:assembleDebug --console=plain -q
exit /b %ERRORLEVEL%
