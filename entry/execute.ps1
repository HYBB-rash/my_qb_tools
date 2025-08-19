<#
    SMB 预认证（不再映射盘符）
    - 目的：在执行 Python 前，先对目标 UNC 共享建立会话，避免权限问题。
    - 用法：将 cfg.json 中的库路径改为 UNC（例如 \\nuc\d\Downloader\Videos\动漫）。
    - 凭据来源：
        1) 优先使用已保存的凭据（cmdkey /add 或现有域令牌）。
        2) 若提供了环境变量 QB_SMB_USER / QB_SMB_PASS，则使用它们。
    - 注意：若遇到 1219（重复会话），会先删除再重连。
#>

$ShareRoot = "\\\nuc\d"            # TODO: 按需修改为你的 NUC 共享根（与 cfg.json 一致）
$User      = $env:QB_SMB_USER   # 例如：home.man-her.tech\file_share 或 NUC\file_share
$Pass      = $env:QB_SMB_PASS   # 例如：你的密码

function Invoke-NetUse($argsString) {
    $null = cmd.exe /c $argsString
    return $LASTEXITCODE
}

# 先尝试使用当前上下文/凭据管理器（无明文密码）
$exit = Invoke-NetUse ("net use `"$ShareRoot`" /persistent:no")
if ($exit -ne 0) {
    # 可能已有冲突会话，先尝试删除
    $null = cmd.exe /c ("net use `"$ShareRoot`" /delete /y")

    if ($User -and $Pass) {
        $exit = Invoke-NetUse ("net use `"$ShareRoot`" /user:$User $Pass /persistent:no")
    } else {
        $exit = Invoke-NetUse ("net use `"$ShareRoot`" /persistent:no")
    }
}

if ($exit -ne 0) {
    throw @"
无法与 $ShareRoot 建立 UNC 会话（未映射盘符）。
请确保：
  A）已在该账号下保存凭据：cmdkey /add:nuc /user:<域或主机\用户> /pass:<密码>
  或
  B）在计划任务/环境中设置 QB_SMB_USER 与 QB_SMB_PASS。
"@
}

# --- 你的原有脚本逻辑从这里开始 ---

# 以脚本自身路径为基准
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$ExecutePy = Join-Path $ScriptDir "src\execute.py"

if (-not (Test-Path $VenvPython)) {
    Write-Error "venv python not found at: $VenvPython"
    exit 1
}

Set-Location -LiteralPath $ScriptDir

# 让 Python 内部 logging 写入单独的日志文件（避免与 Transcript 编码冲突）
$LogDir = Join-Path $ScriptDir "log"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$PyLogFile = Join-Path $LogDir ("run_py_{0}.log" -f $stamp)
$env:MY_QB_TOOLS_LOG_FILE = $PyLogFile

& $VenvPython $ExecutePy

exit $LASTEXITCODE
