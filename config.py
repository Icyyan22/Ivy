
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
        "/ybdy/play?v_id=21612&r_id=80174&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21625&r_id=80198&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21625&r_id=80199&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21625&r_id=80200&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21626&r_id=80201&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21626&r_id=80202&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21626&r_id=80203&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21680&r_id=80281&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21680&r_id=80282&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21680&r_id=80283&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21681&r_id=80284&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21681&r_id=80285&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21682&r_id=80286&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21682&r_id=80287&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21741&r_id=80442&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21741&r_id=80443&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21749&r_id=80461&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21749&r_id=80462&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21749&r_id=80463&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21750&r_id=80464&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21750&r_id=80465&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21750&r_id=80466&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21778&r_id=80540&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80541&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80542&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80543&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80544&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80545&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80546&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80547&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80548&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80549&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80550&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80551&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80552&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80553&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80554&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80555&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80556&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21778&r_id=80557&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21788&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21800&r_id=80589&r=video&t=2&pg=1",
        "/ybdy/play?v_id=21800&r_id=80590&r=video&t=2&pg=1",

        "/ybdy/play?v_id=21817&r=video&t=2",  # 到加强斗争井绳


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

    # 弹窗关闭按钮选择器
    POPUP_CLOSE_SELECTORS = [
        "button:has-text('我知道了')",  # 进入视频页面时的提示按钮
        "button:has-text('继续')",
        "button:has-text('关闭')",
        ".close-btn",
        "[class*='close']"
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

    # ===== 自动登录配置 =====
    # 是否启用自动登录
    AUTO_LOGIN_ENABLED = True

    # 登录凭证（请填写你的账号密码）
    LOGIN_USERNAME = "2022007091"  # 请填写你的账号
    LOGIN_PASSWORD = "Yanwanxuan040119"  # 请填写你的密码

    # 验证码识别 API 配置
    CAPTCHA_API_BASE_URL = "https://yunwu.ai/v1/chat/completions"  # API URL，例如 "https://api.example.com/v1/chat/completions"
    CAPTCHA_API_KEY = "sk-KramS0jsUFUrjCN3SMQRiAaYTdFU2WZpgVzX79e5L9QmSKir"  # 请填写你的 API Key
    CAPTCHA_MODEL = "gemini-2.5-pro"  # 使用的模型

    # 登录页面 XPath 选择器
    LOGIN_USERNAME_XPATH = "/html/body/div/div/div[2]/div[3]/div/div[1]/input"
    LOGIN_PASSWORD_XPATH = "//*[@id='app']/div/div[2]/div[3]/div/div[2]/input"
    LOGIN_CAPTCHA_INPUT_XPATH = "//*[@id='app']/div/div[2]/div[3]/div/div[3]/input"
    LOGIN_CAPTCHA_IMAGE_XPATH = "//*[@id='app']/div/div[2]/div[3]/div/div[3]/img"
    LOGIN_SUBMIT_BUTTON_XPATH = "//*[@id='app']/div/div[2]/div[3]/div/div[4]/button"

    # 验证码识别配置
    CAPTCHA_MAX_RETRIES = 3  # 验证码识别失败最大重试次数
    CAPTCHA_PROMPT = "这是一张验证码图片，由大小写英文字母和数字组成，输出验证码实际的字符串"

    # 登录后等待时间（秒）
    LOGIN_WAIT_AFTER_SUBMIT = 3




