@echo off
setlocal
rem **************************************************
rem テストモード用スケッチをStuduino基板にアップロードする
rem **************************************************

set COM_PORT=
rem 入力要求
set /P COM_PORT="Studuino基板と接続しているCOMポートを指定してください: "
rem 入力値echo
echo 入力した文字は %COM_PORT% です

..\scripts\python.bat upload.py %COM_PORT%

pause
