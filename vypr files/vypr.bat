@echo off
REM Vypr Language Compiler Batch Script

setlocal enabledelayedexpansion

REM Enable ANSI escape sequences for better formatting
REM This allows the separators to display properly
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "10.0" (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 0x00000001 /f > nul 2>&1
)

set KEEP_FLAG=
set VERBOSE_FLAG=
set OUTPUT_FILE=
set INPUT_FILE=

REM Process command line arguments
:parse_args
if "%~1"=="" goto :run_compiler
if /i "%~1"=="-keep" (
    set KEEP_FLAG=-keep
    shift
    goto :parse_args
)
if /i "%~1"=="-verbose" (
    set VERBOSE_FLAG=-verbose
    shift
    goto :parse_args
)
if /i "%~1"=="-o" (
    set OUTPUT_FILE=-o %~2
    shift
    shift
    goto :parse_args
)

REM If the argument doesn't match any flag, it's the input file
set INPUT_FILE=%~1
shift
goto :parse_args

:run_compiler
if "!INPUT_FILE!"=="" (
    echo Error: No input file specified.
    echo Usage: vypr filename.vy [-keep] [-verbose] [-o output_filename]
    exit /b 1
)

REM Run the Python compiler with the parsed arguments
python %~dp0vypr_compiler.py !INPUT_FILE! !KEEP_FLAG! !VERBOSE_FLAG! !OUTPUT_FILE!

exit /b %ERRORLEVEL% 