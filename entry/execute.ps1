# 以脚本自身路径为基准
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$ExecutePy = Join-Path $ScriptDir "src\execute.py"

if (-not (Test-Path $VenvPython)) {
    Write-Error "venv python not found at: $VenvPython"
    exit 1
}

& $VenvPython $ExecutePy

exit $LASTEXITCODE