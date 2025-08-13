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

Set-Location -LiteralPath $ScriptDir

# 准备日志文件：log/ 目录 + 时间戳 + 安全化的种子名
$LogDir = Join-Path $ScriptDir "log"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$safe  = ($Name -replace "[^a-zA-Z0-9._-]","_").Trim()
if ($safe.Length -gt 80) { $safe = $safe.Substring(0,80) }
$LogFile = Join-Path $LogDir ("run_ps_{0}_{1}.log" -f $stamp, $safe)

# 使用 Transcript 捕获包含外部进程在内的所有输出（含 stderr）
$code = $null
Start-Transcript -Path $LogFile -Append | Out-Null
try {
    Write-Host "[start] $(Get-Date -Format s) N='$Name' L='$Category' G='$Tags' F='$ContentPath'"

    # 为确保中文输出正常，强制 python 使用 UTF-8 输出
    $env:PYTHONIOENCODING = 'utf-8'

    # 不需要“激活”会话；直接用 venv 下的 python 执行
    & $VenvPython $EnqueuePy `
        --name $Name `
        --category $Category `
        --tags $Tags `
        --content-path $ContentPath

    $code = $LASTEXITCODE
}
catch {
    $code = 1
    Write-Error $_
}
finally {
    if ($null -eq $code) { $code = $LASTEXITCODE }
    Write-Host ("[end] {0} exit={1}" -f (Get-Date -Format s), $code)
    Stop-Transcript | Out-Null
}

exit $code
