@echo off
setlocal
rem **************************************************
rem �e�X�g���[�h�p�X�P�b�`��Studuino��ɃA�b�v���[�h����
rem **************************************************

set COM_PORT=
rem ���͗v��
set /P COM_PORT="Studuino��Ɛڑ����Ă���COM�|�[�g���w�肵�Ă�������: "
rem ���͒lecho
echo ���͂��������� %COM_PORT% �ł�

..\scripts\python.bat upload.py %COM_PORT%

pause
