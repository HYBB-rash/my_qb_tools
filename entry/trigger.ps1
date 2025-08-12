# trigger.ps1  —— 相对路径推断 venv
param(
    [string]$Name,         # %N
    [string]$Category,     # %L
    [string]$Tags,         # %G
    [string]$ContentPath   # %F
)

$ErrorActionPreference = "Stop"

# 以脚本自身路径为基准
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$EnqueuePy = Join-Path $ScriptDir "src\enqueue.py"

if (-not (Test-Path $VenvPython)) {
    Write-Error "venv python not found at: $VenvPython"
    exit 1
}

# 不需要“激活”会话；直接用 venv 下的 python 执行，最稳
& $VenvPython $EnqueuePy `
    --name $Name `
    --category $Category `
    --tags $Tags `
    --content-path $ContentPath `

exit $LASTEXITCODE