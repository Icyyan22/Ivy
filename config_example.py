"""
示例配置文件
复制此文件并根据您的实际网站进行修改
"""

from config import Config


class ExampleConfig(Config):
    """
    示例配置 - 请根据实际网站修改
    """

    # ===== 基础配置 =====
    # 替换为您的视频网站 URL
    VIDEO_SITE_URL = "https://example-learning-site.com/courses/12345"

    # ===== 选择器配置示例 =====
    # 提示：使用浏览器开发者工具（F12）找到这些选择器

    # 1. 视频列表选择器
    # 示例：<div class="course-video-item">...</div>
    VIDEO_LIST_SELECTOR = ".course-video-item, [class*='video-item']"

    # 2. 主视频播放器选择器
    # 示例：<video class="video-player">...</video>
    MAIN_VIDEO_SELECTOR = ".video-player video, video[class*='player']"

    # 3. 小视频/章节选择器（如果视频有章节）
    # 示例：<div class="chapter-item">...</div>
    MINI_VIDEO_SELECTOR = ".chapter-item video, [class*='chapter'] video"

    # 4. 下一个视频按钮选择器
    # 示例：<button class="next-btn">下一个</button>
    NEXT_VIDEO_BUTTON_SELECTOR = ".next-btn, button:has-text('下一个'), [class*='next']"

    # ===== 弹窗配置示例 =====
    # 弹窗容器选择器
    POPUP_SELECTORS = [
        ".modal",                    # 示例1: <div class="modal">...</div>
        ".popup-container",          # 示例2: <div class="popup-container">...</div>
        "[role='dialog']",          # 示例3: <div role="dialog">...</div>
        "[class*='mask']",          # 示例4: 包含 mask 的 class
    ]

    # 弹窗关闭/确认按钮选择器
    POPUP_CLOSE_SELECTORS = [
        "button:has-text('关闭')",   # 文字为"关闭"的按钮
        "button:has-text('确定')",   # 文字为"确定"的按钮
        "button:has-text('继续学习')", # 文字为"继续学习"的按钮
        "button:has-text('知道了')",  # 文字为"知道了"的按钮
        ".modal-close",              # class 为 modal-close 的元素
        ".btn-confirm",              # class 为 btn-confirm 的元素
        "[class*='close-btn']",      # class 包含 close-btn 的元素
    ]

    # ===== 行为配置 =====
    # 检测间隔（秒）
    POPUP_CHECK_INTERVAL = 2         # 弹窗检测间隔
    FOCUS_CHECK_INTERVAL = 3         # 窗口焦点检测间隔
    VIDEO_STATE_CHECK_INTERVAL = 2   # 视频状态检测间隔

    # 超时配置（秒）
    VIDEO_LOAD_TIMEOUT = 30          # 视频加载超时
    MAX_VIDEO_DURATION = 7200        # 单个视频最大播放时间（2小时）

    # ===== 登录配置（如果需要）=====
    REQUIRE_LOGIN = False            # 是否需要登录

    # 如果需要登录，请配置以下信息
    # 警告：不要在代码中硬编码密码，建议使用环境变量
    # LOGIN_USERNAME = os.getenv("VIDEO_SITE_USERNAME")
    # LOGIN_PASSWORD = os.getenv("VIDEO_SITE_PASSWORD")
    LOGIN_USERNAME = ""
    LOGIN_PASSWORD = ""
    LOGIN_URL = "https://example-learning-site.com/login"

    # 登录表单选择器
    USERNAME_INPUT_SELECTOR = "input[name='username'], input[type='email']"
    PASSWORD_INPUT_SELECTOR = "input[name='password'], input[type='password']"
    LOGIN_BUTTON_SELECTOR = "button[type='submit'], button:has-text('登录')"

    # ===== 调试配置 =====
    HEADLESS = False                 # False=显示浏览器窗口，True=后台运行
    VERBOSE_LOGGING = True           # 是否输出详细日志
    SAVE_SCREENSHOTS = True          # 是否保存错误截图
    SCREENSHOT_DIR = "./screenshots" # 截图保存目录


# ===== 使用示例 =====
# 在 main.py 中使用此配置：
#
# from config_example import ExampleConfig
# automator = VideoAutomator(ExampleConfig())
# await automator.start()


# ===== 如何找到选择器？=====
"""
步骤1: 打开视频网站
步骤2: 按 F12 打开浏览器开发者工具
步骤3: 点击左上角的"选择元素"图标（或按 Ctrl+Shift+C）
步骤4: 鼠标悬停在目标元素上（如视频列表项）
步骤5: 在开发者工具中右键该元素
步骤6: 选择 Copy → Copy selector
步骤7: 粘贴到配置文件中

示例HTML结构：
<div class="course-content">
    <div class="video-list">
        <div class="video-item" data-id="1">
            <video class="player"></video>
            <button class="next-chapter">下一章</button>
        </div>
    </div>
    <div class="modal" style="display: block;">
        <button class="modal-close">关闭</button>
    </div>
</div>

对应的选择器：
VIDEO_LIST_SELECTOR = ".video-item"
MAIN_VIDEO_SELECTOR = ".player"
NEXT_VIDEO_BUTTON_SELECTOR = ".next-chapter"
POPUP_SELECTORS = [".modal"]
POPUP_CLOSE_SELECTORS = [".modal-close"]
"""


# ===== 常见网站选择器参考 =====
"""
1. 学堂在线类网站：
   VIDEO_LIST_SELECTOR = ".course-list-item"
   MAIN_VIDEO_SELECTOR = "#video-player video"

2. 慕课网类网站：
   VIDEO_LIST_SELECTOR = ".chapter-item"
   MAIN_VIDEO_SELECTOR = ".vjs-tech"
   NEXT_VIDEO_BUTTON_SELECTOR = ".next-btn"

3. 腾讯课堂类网站：
   VIDEO_LIST_SELECTOR = ".lesson-item"
   MAIN_VIDEO_SELECTOR = "video[class*='video-player']"

注意：每个网站的HTML结构都不同，请务必根据实际情况修改！
"""
