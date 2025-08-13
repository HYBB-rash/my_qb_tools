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

# 准备日志文件：log/ 目录 + 时间戳 + 安全化的种子名
$LogDir = Join-Path $ScriptDir "log"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$safe  = ($Name -replace "[^a-zA-Z0-9._-]","_").Trim()
if ($safe.Length -gt 80) { $safe = $safe.Substring(0,80) }
$LogFile = Join-Path $LogDir ("run_{0}_{1}.log" -f $stamp, $safe)

# 记录开头信息
$startLine = "[start] $(Get-Date -Format s) N='$Name' L='$Category' G='$Tags' F='$ContentPath'"
Add-Content -Path $LogFile -Value $startLine

# 不需要“激活”会话；直接用 venv 下的 python 执行，输出重定向到日志
& $VenvPython $EnqueuePy `
    --name $Name `
    --category $Category `
    --tags $Tags `
    --content-path $ContentPath `
    *>> $LogFile

$code = $LASTEXITCODE
Add-Content -Path $LogFile -Value ("[end] $(Get-Date -Format s) exit=$code")
exit $code
