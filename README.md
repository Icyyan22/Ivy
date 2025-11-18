# 视频学习网站自动化脚本

一个基于 Python + Playwright 的视频学习网站自动化脚本，能够自动播放视频列表、处理弹窗、保持窗口焦点等。

## 功能特性

✅ **自动播放视频列表** - 自动遍历并播放所有主视频
✅ **小视频章节切换** - 自动检测并切换右侧小视频章节
✅ **智能弹窗处理** - 自动检测并关闭确认/继续类弹窗
✅ **窗口焦点保持** - 保持浏览器窗口在最上层，防止自动暂停
✅ **视频状态监控** - 实时监测播放状态，自动恢复播放
✅ **反检测配置** - 隐藏 WebDriver 特征，模拟真实用户
✅ **多平台支持** - 支持 macOS, Windows, Linux

## 环境要求

- Python 3.8+
- macOS / Windows / Linux
- 稳定的网络连接

## 安装步骤

### 1. 克隆或下载项目

```bash
cd video_automation
```

### 2. 使用 uv 安装依赖

推荐使用 [uv](https://github.com/astral-sh/uv) 快速安装依赖：

```bash
# 安装所有依赖
uv sync

# macOS 用户额外安装窗口管理依赖
uv sync --extra macos
```

**或者使用传统 pip 方式**：

```bash
# 安装核心依赖
uv pip install -e .

# macOS 用户额外安装
uv pip install -e ".[macos]"
```

### 3. 安装 Playwright 浏览器

```bash
uv run playwright install chromium
```

### 4. macOS 额外配置（窗口管理）

如果需要窗口焦点保持功能，需要授权终端/IDE 的辅助功能权限：

1. 打开「系统设置」→「隐私与安全性」→「辅助功能」
2. 添加并勾选您使用的终端应用（Terminal.app / iTerm 等）

## 配置说明

### 核心配置

打开 `config.py` 文件，修改以下关键配置：

#### 1. 视频网站 URL

```python
VIDEO_SITE_URL = "https://your-video-site.com/course"
```

将其修改为您的实际视频学习网站地址。

#### 2. 选择器配置（重要！）

使用浏览器开发者工具（F12）找到对应的 CSS 选择器：

```python
# 视频列表项选择器
VIDEO_LIST_SELECTOR = ".video-list-item, [class*='video-item']"

# 主视频播放器选择器
MAIN_VIDEO_SELECTOR = "video, .video-player video"

# 小视频播放器选择器（如果有）
MINI_VIDEO_SELECTOR = ".mini-video video"

# 下一个视频按钮选择器
NEXT_VIDEO_BUTTON_SELECTOR = ".next-video, button:has-text('下一个')"
```

#### 3. 弹窗选择器

根据网站的弹窗样式修改：

```python
# 弹窗容器选择器
POPUP_SELECTORS = [
    ".popup",
    ".modal",
    "[role='dialog']"
]

# 弹窗关闭/确认按钮选择器
POPUP_CLOSE_SELECTORS = [
    "button:has-text('关闭')",
    "button:has-text('确定')",
    "button:has-text('继续')",
    ".close-btn"
]
```

### 如何获取选择器？

1. 打开视频网站
2. 按 F12 打开开发者工具
3. 点击"选择元素"按钮（或按 Ctrl+Shift+C）
4. 鼠标悬停在要选择的元素上
5. 在开发者工具中右键 → Copy → Copy selector

### 可选配置

```python
# 是否需要登录
REQUIRE_LOGIN = False

# 如果需要登录，配置用户名密码
LOGIN_USERNAME = "your_username"
LOGIN_PASSWORD = "your_password"
LOGIN_URL = "https://your-site.com/login"

# 调试选项
VERBOSE_LOGGING = True      # 详细日志
SAVE_SCREENSHOTS = True     # 保存错误截图
HEADLESS = False            # 无头模式（False=显示浏览器）
```

## 使用方法

### 1. 基础使用

```bash
python main.py
```

或者：

```bash
python3 main.py
```

### 2. 运行流程

1. 脚本会显示启动横幅和当前配置
2. 确认配置无误后输入 `y` 开始
3. 浏览器窗口会自动打开
4. 脚本会自动完成所有视频播放
5. 按 `Ctrl+C` 可随时中断

### 3. 日志和输出

- **控制台输出**: 实时显示运行状态
- **日志文件**: `video_automation.log`
- **错误截图**: `screenshots/` 目录

## 项目结构

```
video_automation/
├── main.py                  # 主程序入口
├── video_automator.py       # 核心自动化类
├── popup_handler.py         # 弹窗处理模块
├── window_manager.py        # 窗口焦点管理
├── config.py                # 配置文件
├── config_example.py        # 配置示例
├── test_selectors.py        # 选择器测试工具
├── pyproject.toml           # 项目配置和依赖
├── README.md                # 使用说明
├── QUICKSTART.md            # 快速开始指南
├── .gitignore               # Git 忽略文件
├── video_automation.log     # 运行日志（自动生成）
└── screenshots/             # 错误截图（自动生成）
```

## 工作原理

### 核心流程

```
启动浏览器
    ↓
访问目标网站
    ↓
[可选] 登录
    ↓
获取视频列表
    ↓
遍历每个视频
    ├→ 点击视频
    ├→ 等待加载
    ├→ 播放主视频/章节
    ├→ 自动切换小视频
    └→ 等待播放完成
    ↓
所有视频完成
```

### 并发任务

脚本同时运行以下监控任务：

1. **主播放循环** - 控制视频播放流程
2. **弹窗监测** - 每 2 秒检测一次弹窗
3. **窗口焦点保持** - 每 3 秒检查一次窗口焦点
4. **视频状态监测** - 每 2 秒检查视频是否暂停

## 常见问题

### 1. 找不到视频列表

**问题**: 脚本提示"未找到视频列表"

**解决**:
- 检查 `VIDEO_LIST_SELECTOR` 配置是否正确
- 使用浏览器开发者工具验证选择器
- 增加 `VIDEO_LOAD_TIMEOUT` 超时时间

### 2. 弹窗无法关闭

**问题**: 弹窗出现但脚本无法关闭

**解决**:
- 检查 `POPUP_CLOSE_SELECTORS` 配置
- 在弹窗出现时使用开发者工具查看按钮选择器
- 添加更多可能的选择器到配置中

### 3. 视频播放不完整

**问题**: 视频还没播放完就跳到下一个

**解决**:
- 调整 `VIDEO_END_THRESHOLD` 阈值
- 检查视频选择器是否正确
- 查看日志确认播放状态检测是否正常

### 4. 窗口焦点丢失

**问题**: macOS 上窗口焦点保持不生效

**解决**:
- 确认已授予终端「辅助功能」权限
- 检查 AppleScript 是否可以正常执行
- 手动测试: `osascript -e 'tell application "System Events" to get name of processes'`

### 5. 浏览器被检测为自动化

**问题**: 网站提示"检测到自动化工具"

**解决**:
- 脚本已内置反检测配置
- 如果仍被检测，可能需要：
  - 使用代理
  - 添加 Cookie
  - 模拟更多人工操作（随机延迟等）

### 6. macOS 依赖安装失败

**问题**: `pip install` 时 pyobjc 安装失败

**解决**:
```bash
# 使用 homebrew 安装依赖
brew install python-tk

# 单独安装 pyobjc
pip install --upgrade pip setuptools wheel
pip install pyobjc-framework-Cocoa
pip install pyobjc-framework-Quartz
```

## 高级使用

### 1. 自定义配置类

```python
from config import Config

class MyConfig(Config):
    VIDEO_SITE_URL = "https://my-site.com"
    POPUP_CHECK_INTERVAL = 1  # 更频繁的检测

# 使用自定义配置
from video_automator import VideoAutomator
automator = VideoAutomator(MyConfig())
await automator.start()
```

### 2. 单独使用模块

```python
# 只使用弹窗处理器
from popup_handler import PopupHandler
from config import Config

handler = PopupHandler(Config())
await handler.monitor_popups(page, check_interval=2)
```

### 3. 调试模式

在 `config.py` 中启用详细日志：

```python
VERBOSE_LOGGING = True
SAVE_SCREENSHOTS = True
```

然后查看日志文件 `video_automation.log` 了解详细执行过程。

## 技术栈

- **Playwright** - 浏览器自动化框架
- **Python asyncio** - 异步编程
- **pyobjc** (macOS) - 窗口管理
- **logging** - 日志系统

## 安全提示

⚠️ **重要**:

1. 不要在配置文件中直接写入真实密码
2. 使用环境变量存储敏感信息：

```python
import os
LOGIN_USERNAME = os.getenv("VIDEO_SITE_USERNAME")
LOGIN_PASSWORD = os.getenv("VIDEO_SITE_PASSWORD")
```

3. 不要将包含敏感信息的 `config.py` 提交到 Git
4. 仅用于个人学习用途，请遵守网站服务条款

## 性能优化建议

1. **减少检测频率**: 适当增加 `POPUP_CHECK_INTERVAL` 等间隔时间
2. **禁用无用功能**: 如果不需要窗口焦点保持，可以注释相关代码
3. **使用 headless 模式**: 设置 `HEADLESS = True` 节省资源（但可能导致自动暂停）

## 限制说明

- 本脚本需要网站允许自动化访问
- 某些强反爬网站可能无法使用
- 视频播放依赖网站的 HTML5 video 标签
- 窗口焦点保持功能需要系统权限

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 更新日志

### v1.0 (2025-01)

- ✅ 初始版本发布
- ✅ 支持基础视频自动播放
- ✅ 支持弹窗处理
- ✅ 支持窗口焦点保持
- ✅ 支持 macOS / Windows / Linux

## 联系方式

如有问题或建议，欢迎提交 Issue。

---

**Happy Learning! 🎓**
