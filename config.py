
"""
配置文件
包含所有可配置的参数
"""

class Config:
    """视频自动化配置类"""

    # ===== 网站配置 =====
    # 视频学习网站的基础URL
    VIDEO_SITE_URL = "http://tyut.dangqipiaopiao.com/"

    # 视频列表 - 相对路径的href列表
    # 例如: ["/course/video/1", "/course/video/2"]
    VIDEO_HREF_LIST = [
        "/ybdy/play?v_id=21612&r_id=80173&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21612&r_id=80174&r=video&t=2&pg=1"
    ]

    # ===== 选择器配置 (需要根据实际网站修改) =====
    # 视频播放器选择器
    VIDEO_PLAYER_SELECTOR = "video"

    # "继续"按钮选择器（中途弹窗）
    CONTINUE_BUTTON_SELECTOR = "button:has-text('继续')"

    # "视频播放完成"弹窗选择器
    COMPLETE_POPUP_SELECTOR = ".popup:has-text('视频播放完成'), .modal:has-text('视频播放完成'), [class*='complete']"

    # 通用弹窗选择器（用于检测任何弹窗）
    POPUP_SELECTORS = [
        ".popup",
        ".modal",
        ".dialog",
        "[role='dialog']",
        "[class*='mask']",
        "[class*='overlay']"
    ]

    # ===== 浏览器配置 =====
    # 是否使用无头模式 (False=显示浏览器窗口，推荐False以便手动登录)
    HEADLESS = False

    # 浏览器窗口大小
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080

    # User-Agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # ===== 行为配置 =====
    # 弹窗检测间隔 (秒)
    POPUP_CHECK_INTERVAL = 3

    # 视频完成后等待时间 (秒)
    VIDEO_COMPLETE_WAIT = 5

    # 单个视频最大播放时间 (秒, 防止卡死)
    MAX_VIDEO_DURATION = 3600  # 1小时

    # 点击播放后等待视频启动的时间 (秒)
    PLAY_START_WAIT = 2

    # ===== 调试配置 =====
    # 是否启用详细日志
    VERBOSE_LOGGING = True

    # 是否保存截图 (出错时)
    SAVE_SCREENSHOTS = True

    # 截图保存目录
    SCREENSHOT_DIR = "./screenshots"




