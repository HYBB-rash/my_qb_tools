# --- SMB 映射：确保本会话可用 Y: 指向指定共享（计划任务友好） ---
$Drive = 'Y:'
$Share = '\\home.man-her.tech\d'   # TODO: 按需修改共享名
# 可选：在计划任务里给这个账号设置环境变量 QB_SMB_USER / QB_SMB_PASS，则会用它们登录
$User  = $env:QB_SMB_USER          # 例如：home.man-her.tech\file_share
$Pass  = $env:QB_SMB_PASS          # 例如：你的密码

# 如果 Y: 已映射但不是我们需要的共享，先删除
$y = Get-PSDrive -PSProvider FileSystem -Name ($Drive.TrimEnd(':')) -ErrorAction SilentlyContinue
if ($y) {
    if ($y.Root -notlike "$Share*") {
        cmd.exe /c "net use $Drive /delete /y" | Out-Null
        $y = $null
    }
}

# 若还未映射，则尝试映射
if (-not $y) {
    # 1) 先尝试使用当前登录令牌/凭据管理器里的凭据（推荐：提前执行一次 cmdkey /add 保存）
    $cmd = "net use $Drive `"$Share`" /persistent:no"
    $null = cmd.exe /c $cmd
    if ($LASTEXITCODE -ne 0) {
        # 2) 若失败且提供了环境变量，则带用户名/密码再试一次
        if ($User -and $Pass) {
            $cmd = "net use $Drive `"$Share`" /user:$User $Pass /persistent:no"
            $null = cmd.exe /c $cmd
        }
    }

    # 3) 仍失败则直接报错（避免后续 Y:\ 路径全部失败但原因不明）
    if ($LASTEXITCODE -ne 0) {
        throw @"
无法将 $Drive 映射到 $Share。
请在“运行该计划任务的账号”下先保存凭据一次，或在任务里提供环境变量：
  方式A（推荐）：cmdkey /add:home.man-her.tech /user:home.man-her.tech\file_share /pass:<密码>
  方式B：在计划任务的环境中设置 QB_SMB_USER=home.man-her.tech\file_share 和 QB_SMB_PASS=<密码>
"@
    }
}

# （可选）此处可以验证一下
# if (-not (Test-Path "$Drive\")) { throw "Y: 映射成功但不可访问：$Share" }

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
$PyLogFile = Join-Path $LogDir ("run_py_{0}.log" -f $stamp)
$env:MY_QB_TOOLS_LOG_FILE = $PyLogFile

& $VenvPython $ExecutePy

exit $LASTEXITCODE