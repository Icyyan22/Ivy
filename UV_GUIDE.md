# 使用 UV 管理依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 作为依赖管理工具，提供更快的安装速度。

## 安装 uv

如果您还没有安装 uv：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 使用 pip
pip install uv
```

## 常用命令

### 安装依赖

```bash
# 安装所有依赖（推荐）
uv sync

# macOS 用户额外安装窗口管理依赖
uv sync --extra macos
```

### 运行脚本

```bash
# 方式1: 直接运行
uv run python main.py

# 方式2: 激活虚拟环境后运行
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
python main.py
```

### 安装 Playwright 浏览器

```bash
uv run playwright install chromium
```

### 添加新依赖

```bash
# 添加运行时依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 添加可选依赖
uv add --optional macos package-name
```

### 更新依赖

```bash
# 更新所有依赖
uv sync --upgrade

# 更新特定包
uv add package-name@latest
```

### 锁定依赖版本

```bash
# 生成 uv.lock 文件（自动）
uv sync
```

## 项目依赖说明

### 核心依赖

- **playwright** - 浏览器自动化框架
- **python-dotenv** - 环境变量管理

### 可选依赖（macOS）

- **pyobjc-framework-Cocoa** - macOS 窗口管理
- **pyobjc-framework-Quartz** - macOS Quartz 支持

仅在 macOS 上需要安装：

```bash
uv sync --extra macos
```

## 虚拟环境

uv 会自动创建和管理虚拟环境：

```bash
# 虚拟环境位置
.venv/

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 退出虚拟环境
deactivate
```

## 传统 pip 方式（备选）

如果您不想使用 uv，也可以使用传统的 pip：

```bash
# 从 pyproject.toml 安装
pip install -e .

# macOS 用户
pip install -e ".[macos]"
```

## 配置文件

项目配置在 `pyproject.toml` 中：

```toml
[project]
name = "video-automation"
version = "1.0.0"
dependencies = [
    "playwright>=1.40.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
macos = [
    "pyobjc-framework-Cocoa>=10.1",
    "pyobjc-framework-Quartz>=10.1",
]
```

## 常见问题

### Q: uv sync 很慢怎么办？

A: uv 通常比 pip 快很多。如果慢，可能是网络问题，可以尝试：

```bash
# 使用国内镜像
export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
uv sync
```

### Q: 如何查看已安装的包？

```bash
uv pip list
```

### Q: 如何卸载包？

```bash
uv remove package-name
```

### Q: 遇到依赖冲突怎么办？

```bash
# 重新解析依赖
uv sync --reinstall
```

## 更多信息

- uv 官方文档: https://github.com/astral-sh/uv
- Python 包索引: https://pypi.org/
