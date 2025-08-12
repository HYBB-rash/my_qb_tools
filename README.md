# my_qb_tools

基于 qBittorrent 下载后的个人媒体整理小工具：将下载内容按 TMDB 信息与自定义规则硬链接到媒体库、生成 `tvshow.nfo`，并通过 tinyMediaManager（TMM）完成刮削与重命名。任务流转与配置均保存在本地 SQLite 数据库，支持轻量的 TTL 锁以避免并发冲突。

> 当前项目以个人需求为主，重点支持 Windows（TMM 路径为 Windows 安装位置）；其他平台可运行核心功能（如入队、DB、硬链），但未内置 TMM 路径与跨盘硬链回退。

## 功能特性

- 媒体整理流水线：下载目录 → 入队（包含季与 TMDB 信息） → 媒体库目录硬链接 → 生成 `tvshow.nfo` → TMM 刮削/重命名
- TMDB 元数据：按 `tmdb_id` 获取剧名（需 `TMDB_API_TOKEN`）
- 可扩展的“移动策略工厂”：按 key（`tmdb-<id>-s<season>`）注册不同整理策略
- SQLite 本地存储：任务表（task）、配置表（cfg）、锁表（locks）
- 统一日志格式，支持（可选）Telegram 推送

## 目录结构

- `src/enqueue.py`：CLI 入队脚本
- `src/execute.py`：CLI 执行脚本（弹出最早未处理任务并处理）
- `src/new_cfg.py`：CLI 初始化/新增 cfg 记录脚本
- `src/tools/`：业务逻辑（DB、服务、移动策略、qb、数据模型）
- `src/share/`：日志、Result 类型、Telegram handler
- `entry/*.ps1`：Windows 环境触发脚本示例
- `cfg.json`：默认配置（例如类目到媒体库路径映射）
- `data/app.db`：SQLite 数据库（运行后生成）
- `test/`：无网络依赖的单元测试（pytest）

## 安装与准备

1) 环境

- Python 3.12+
- Windows（完整体验；TMM 调用依赖 Windows 安装路径）

2) 安装依赖（二选一）

- 简单方式（pip）：
  - `pip install python-dotenv requests python-qbittorrent pytest`
- 或使用项目配置（需构建工具支持）：
  - 你也可以按自己的工具链（uv/pdm/hatch/poetry）安装 `pyproject.toml` 中声明的依赖

3) 配置环境变量（根目录 `.env`，已加入 `.gitignore`）

```
QBIT_URL=http://<your-qb-host>:8080
QBIT_USER=<user>
QBIT_PASSWORD=<password>
TMDB_API_TOKEN=<your_tmdb_v4_bearer>

# 可选：日志推送
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_CHAT_ID=<chat_id>
```

4) 配置默认 cfg（根目录 `cfg.json`）

最常用字段为类目与媒体库路径映射，例如：

```json
{
  "category_mapping": {
    "电视剧": "D:/Media/TV",
    "电影": "D:/Media/Movies"
  }
}
```

## 快速开始

1) 将 cfg 写入数据库（或使用 `cfg.json` 默认值）

```
python src/new_cfg.py --season 1 --tmdb_id 243224
# 或带自定义 cfg：
python src/new_cfg.py --season 1 --tmdb_id 243224 --cfg '{"category_mapping": {"电视剧": "D:/Media/TV"}}'
```

2) 入队一个整理任务

```
python src/enqueue.py \
  --name "The Movie 2024 1080p WEB-DL" \
  --category "电视剧" \
  --tags "season=01,tmdb=243224-凡人修仙传" \
  --content-path "D:/Downloads/电视剧/凡人修仙传.S01E27.2160p.WEB-DL.mp4"
```

- `tags` 语法：
  - `season=<int>`
  - `tmdb=<id>-<title>`（title 中允许 `-`，内部按 `split('-', 1)` 解析）

3) 执行整理（弹出最早未处理的任务并执行一次完整流水线）

```
python src/execute.py
```

流程包含：
- 读取 cfg，解析类目根目录
- 基于 TMDB id 获取剧名，拼接目标路径 `<root>/<tv_show_name>/season <N>`
- 生成 `tvshow.nfo`（包含 `<uniqueid type="tmdb">`）
- 调用移动策略函数（硬链接）
- 调用 TMM CLI 刮削与重命名（Windows）

> 注意：硬链接需要源与目标位于同一文件系统；跨盘/网络盘会失败（当前不回退为复制）。

## 移动策略工厂（自定义整理规则）

策略以工厂模式注册，key 形如 `tmdb-<id>-s<season>`。

示例：`src/tools/move/implementations.py`

```python
from pathlib import Path
from share import Factory
from tools.move.interfaces import Mover

factory: Factory[Mover] = Factory()

@factory.register("tmdb-243224-s1")
def mover_tmdb_243224_s1(where: Path, to: Path) -> None:
    # 选择一个正则来挑选要硬链的文件
    from tools.move.implementations import default_move
    mover = default_move(r"凡人修仙传")
    return mover(where, to)
```

在服务中调用：

```python
mover = MOVE_FACTORY.create(f"tmdb-{tmdb_id}-s{season}")
mover(content_path, destination)
```

> 设计约定：如果没有找到匹配策略，程序会抛出异常，以便你决定这是“参数错误”还是应为新场景新增实现。

## 锁与执行模型

- `locks` 表实现 TTL 锁，用于 `execute`/`create_cfg` 等入口，避免并发跑重复任务
- 发生异常时，锁可能不会主动释放（设计用于倒逼排查与副作用清理），也可通过超时自然过期

## 日志

- 控制台输出：`[LEVEL]-[ts]-[name=>func, file:line]: message`
- 可选 Telegram 推送：设置 `TELEGRAM_BOT_TOKEN` 与 `TELEGRAM_CHAT_ID`

## 测试

项目内置了一批无网络依赖的单测（临时目录 + 本地 SQLite）：

```
pytest -q
```

覆盖点：
- DB 更新时间戳（`updated_at`）
- 工厂注册/默认/未知键路径
- `tvshow.nfo` 写入
- 硬链接创建
- cfg/任务读写与服务层行为（通过伪造数据/猴子补丁）

## 常见问题（FAQ）

- Q: 运行时报 `MoveFunctionNotFound`？
  - A: 为设计预期。请在 `src/tools/move/implementations.py` 中为该 `tmdb-<id>-s<season>` 注册实现，或检查入队参数。
- Q: TMM 未找到？
  - A: 仅支持 Windows 默认安装路径。请手动安装 TMM5 或修改 `get_tmm_cmd` 返回路径。
- Q: 硬链失败？
  - A: 确保源/目标在同一文件系统；跨盘符不支持硬链。

## 免责声明

本项目为个人用途，不保证向后兼容性与完整跨平台支持。请在确认行为符合你的预期后再批量使用。
