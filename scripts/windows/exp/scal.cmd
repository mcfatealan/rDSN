SET exp_dir=%~dp0
SET bin_root=%~dp0bin
SET test_app=%1
SET cluster=%2

if "%1" EQU "simple_kv" (
    SET test_app_upper=simple_kv
    SET dll_name=dsn.replication.simple_kv.module.dll
)
    
if "%1" EQU "leveldb" (
    SET test_app_upper=LevelDb
    SET dll_name=dsn.apps.LevelDb.dll
)

if "%1" EQU "xlock" (
    SET test_app_upper=XLock
    SET dll_name=dsn.apps.XLock.dll
)

if "%1" EQU "kyotocabinet" (
    SET test_app_upper=KyotoCabinet
    SET dll_name=dsn.apps.KyotoCabinet.dll
)


if "%1" EQU "redis" (
    SET test_app_upper=redis
    SET dll_name=redis.dll
)

if "%1" EQU "rrdb" (
    SET test_app_upper=rrdb
    SET dll_name=rrdb.dll
)


if "%test_app_upper%" EQU "" (
    CALL %bin_dir%\echoc.exe 4  no such app %1 for perf test, please check spelling
    GOTO:EOF
)


IF NOT EXIST "%bin_root%\dsn.core.dll" (
    CALL %bin_dir%\echoc.exe 4  %bin_root%\dsn.core.dll not exist, please copy it from DSN_ROOT repo
    GOTO:EOF
)

IF NOT EXIST "%bin_root%\%dll_name%" (
    CALL %bin_dir%\echoc.exe 4  %bin_root%\%dll_name% not exist, please copy it from bondex repo
    GOTO:EOF
)

IF NOT EXIST "%bin_root%\dsn.svchost.exe" (
    CALL %bin_dir%\echoc.exe 4  %bin_root%\dsn.svchost.exe not exist, please copy it from rdsn builder repo
    GOTO:EOF
)

IF NOT EXIST "%bin_root%\dsn.meta_server.dll" (
    CALL %bin_dir%\echoc.exe 4  %bin_root%\dsn.meta_server.dll not exist, please copy it from rdsn builder repo
    GOTO:EOF
)

IF NOT EXIST "%bin_root%\dsn.layer2.stateful.type1.dll" (
    CALL %bin_dir%\echoc.exe 4  %bin_root%\dsn.layer2.stateful.type1.dll not exist, please copy it from rdsn builder repo
    GOTO:EOF
)

IF NOT EXIST "%exp_dir%cluster\%cluster%.ini" (
    CALL %bin_dir%\echoc.exe 4  %exp_dir%cluster\%cluster%.ini not exist, please see the detailed instructions in the cluster folder
    GOTO:EOF
)

IF NOT EXIST "%exp_dir%cluster\%cluster%.scal.meta.txt" (
    CALL %bin_dir%\echoc.exe 4  %exp_dir%cluster\%cluster%.scal.meta.txt not exist, please see the detailed instructions in the cluster folder
    GOTO:EOF
)

IF NOT EXIST "%exp_dir%cluster\%cluster%.scal.replica.txt" (
    CALL %bin_dir%\echoc.exe 4  %exp_dir%cluster\%cluster%.scal.replica.txt not exist, please see the detailed instructions in the cluster folder
    GOTO:EOF
)

IF NOT EXIST "%exp_dir%cluster\%cluster%.scal.client.txt" (
    CALL %bin_dir%\echoc.exe 4  %exp_dir%cluster\%cluster%.scal.client.txt not exist, please see the detailed instructions in the cluster folder
    GOTO:EOF
)

for /f "delims=" %%x in (%exp_dir%\cluster\%cluster%.ini) do (set "%%x")

< %exp_dir%cluster\%cluster%.scal.meta.txt (
    set /p meta_address=
)


@mkdir "%exp_dir%log"
@mkdir "%exp_dir%log\layer2"
@mkdir "%exp_dir%log\layer2\%test_app_upper%"
SET log_dir=%exp_dir%log\layer2\%test_app_upper%

@mkdir "%exp_dir%layer2_test"
@rmdir /Q /S "%exp_dir%layer2_test\%test_app_upper%"
@mkdir "%exp_dir%layer2_test\%test_app_upper%"
SET app_dir=%exp_dir%layer2_test\%test_app_upper%
@mkdir "%app_dir%\meta"
@mkdir "%app_dir%\replica"
@mkdir "%app_dir%\client.perf"

copy /Y %exp_dir%\cluster\%cluster%.scal.meta.txt %app_dir%\meta\machines.txt
copy /Y %exp_dir%\cluster\%cluster%.scal.replica.txt %app_dir%\replica\machines.txt
copy /Y %exp_dir%\cluster\%cluster%.scal.client.txt %app_dir%\client.perf\machines.txt

copy /Y %exp_dir%config\layer2\%test_app_upper%\config.ini %app_dir%\meta\config.ini
copy /Y %exp_dir%config\layer2\%test_app_upper%\config.ini %app_dir%\replica\config.ini
copy /Y %exp_dir%config\layer2\%test_app_upper%\config-webstudio.ini %app_dir%\client.perf\config.ini

copy /Y %bin_root%\*.* %app_dir%\meta
copy /Y %bin_root%\*.* %app_dir%\replica
copy /Y %bin_root%\*.* %app_dir%\client.perf

xcopy  /F /Y /S %exp_dir%WebStudio\* %app_dir%\client.perf

(
    ECHO meta
    ECHO replica
    ECHO client.perf
)  > %app_dir%\apps.txt

(
    ECHO SET ldir=%%~dp0
    ECHO cd /d ldir
    ECHO set i=0
    ECHO :loop
    ECHO     set /a i=%%i%%+1
    ECHO     echo run %%i%%th ... ^>^> ./running.txt
    ECHO     .\dsn.svchost.exe config.ini -app_list meta -cargs meta_address=%meta_address%
    ECHO     ping -n 16 127.0.0.1 ^>nul
    ECHO goto loop
)  > %app_dir%\meta\start.cmd

(
    ECHO SET ldir=%%~dp0
    ECHO cd /d ldir
    ECHO set i=0
    ECHO :loop
    ECHO     set /a i=%%i%%+1
    ECHO     echo run %%i%%th ... ^>^> ./running.txt
    ECHO     .\dsn.svchost.exe config.ini -app_list replica@1 -cargs meta_address=%meta_address%
    ECHO     ping -n 16 127.0.0.1 ^>nul
    ECHO goto loop
)  > %app_dir%\replica\start.cmd

(
    ECHO SET ldir=%%~dp0
    ECHO cd /d ldir
    ECHO set i=0
    ECHO :loop
    ECHO     set /a i=%%i%%+1
    ECHO     echo run %%i%%th ... ^>^> ./running.txt
    ECHO     .\dsn.svchost.exe config.ini -app_list client.perf.test;webstudio -cargs meta_address=%meta_address%
    ECHO     ping -n 16 127.0.0.1 ^>nul
    ECHO goto loop
)  > %app_dir%\client.perf\start.cmd

CALL %bin_dir%\echoc.exe 3 *****TEST [SCAL.TEST] [simple_kv] BEGIN***** 

CALL %bin_dir%"\deploy.cmd" stop %app_dir% %local_path%
ping -n 4 127.0.0.1
CALL %bin_dir%"\deploy.cmd" cleanup %app_dir% %local_path%
CALL %bin_dir%\echoc.exe 3 *****STOPING AND CLEANUPING...***** 

if "%ifauto%" EQU "auto" (
    ping -n %l2stateful_stop_and_cleanup_wait_duration% 127.0.0.1
) else (
    CALL %bin_dir%\echoc.exe 3 *****PRESS ENTER AFTER DONE***** 
    PAUSE
)

CALL %bin_dir%"\deploy.cmd" deploy %app_dir% %local_path%
CALL %bin_dir%\echoc.exe 3 *****DEPOLYING...***** 

if "%ifauto%" EQU "auto" (
    ping -n %l2stateful_deploy_wait_duration% 127.0.0.1
) else (
    CALL %bin_dir%\echoc.exe 3 *****PRESS ENTER AFTER DONE***** 
    PAUSE
)

CALL %bin_dir%"\deploy.cmd" start %app_dir% %local_path%
CALL %bin_dir%\echoc.exe 3 *****STARTING...***** 

CALL %bin_dir%\echoc.exe 3 *****PRESS ENTER TO STOP***** 
PAUSE

CALL %bin_dir%"\deploy.cmd" stop %app_dir% %local_path%
goto end

:end
    CALL %bin_dir%\echoc.exe 3 *****TEST [SCAL.TEST] [simple_kv] END***** 




