# 以脚本自身路径为基准
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$ExecutePy = Join-Path $ScriptDir "src\execute.py"

if (-not (Test-Path $VenvPython)) {
    Write-Error "venv python not found at: $VenvPython"
    exit 1
}

# 让 Python 内部 logging 写入单独的日志文件（避免与 Transcript 编码冲突）
$LogDir = Join-Path $ScriptDir "log"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$PyLogFile = Join-Path $LogDir ("run_py_{0}.log" -f $stamp)
$env:MY_QB_TOOLS_LOG_FILE = $PyLogFile

& $VenvPython $ExecutePy

exit $LASTEXITCODE