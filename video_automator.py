"""
视频自动化核心模块 - 简化版
支持手动登录 + 自动播放视频列表
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from config import Config
from popup_handler import PopupHandler

logger = logging.getLogger(__name__)


class VideoAutomator:
    """视频自动化器 - 简化版"""

    def __init__(self, config: Config = None):
        """
        初始化视频自动化器

        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.popup_handler = PopupHandler(self.config)

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.session_active = False
        self.videos_completed = 0
        self.total_videos = len(self.config.VIDEO_HREF_LIST)

        # 创建截图目录
        if self.config.SAVE_SCREENSHOTS:
            Path(self.config.SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

        logger.info("视频自动化器初始化完成")

    async def start(self):
        """启动自动化流程"""
        logger.info("=" * 60)
        logger.info("视频自动化脚本启动 (简化版)")
        logger.info("=" * 60)

        async with async_playwright() as p:
            # 启动浏览器
            self.browser = await self._launch_browser(p)
            self.context = await self._setup_context(self.browser)
            self.page = await self.context.new_page()

            try:
                self.session_active = True

                # 步骤1: 打开登录页面，等待用户手动登录
                await self._manual_login_flow()

                # 步骤2: 遍历并播放视频列表
                await self._play_video_list()

                logger.info("\n✅ 所有视频播放完成！")

            except KeyboardInterrupt:
                logger.info("\n用户中断，正在退出...")
            except Exception as e:
                logger.error(f"自动化流程出错: {e}", exc_info=True)
                await self._save_screenshot("error")
            finally:
                await self._cleanup()

        logger.info("=" * 60)
        logger.info(f"完成视频: {self.videos_completed}/{self.total_videos}")
        logger.info("=" * 60)

    async def _launch_browser(self, playwright) -> Browser:
        """启动浏览器"""
        logger.info(f"启动浏览器 (headless={self.config.HEADLESS})...")
        logger.info("使用系统已安装的 Chrome 浏览器")

        browser = await playwright.chromium.launch(
            headless=self.config.HEADLESS,
            channel="chrome",  # 使用系统已安装的 Chrome
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        logger.info("浏览器启动成功")
        return browser

    async def _setup_context(self, browser: Browser) -> BrowserContext:
        """设置浏览器上下文"""
        logger.info("配置浏览器上下文...")

        context = await browser.new_context(
            viewport={
                'width': self.config.VIEWPORT_WIDTH,
                'height': self.config.VIEWPORT_HEIGHT
            },
            user_agent=self.config.USER_AGENT,
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        # 注入反检测脚本
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        logger.info("浏览器上下文配置完成")
        return context

    async def _manual_login_flow(self):
        """手动登录流程"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 1: 手动登录")
        logger.info("=" * 60)

        # 打开登录页面
        logger.info(f"正在打开登录页面: {self.config.VIDEO_SITE_URL}")
        await self.page.goto(self.config.VIDEO_SITE_URL, wait_until='networkidle')

        # 等待用户手动登录
        print("\n" + "="* 60)
        print("📌 请在浏览器中手动完成登录（包括验证码）")
        print("📌 登录成功后，请回到命令行")
        print("=" * 60)

        input("\n按回车键继续...")

        logger.info("✅ 用户确认已登录，继续执行...")
        await asyncio.sleep(2)  # 等待页面稳定

    async def _play_video_list(self):
        """播放视频列表"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 2: 自动播放视频列表")
        logger.info("=" * 60)

        if not self.config.VIDEO_HREF_LIST:
            logger.warning("⚠️  VIDEO_HREF_LIST 为空，请在 config.py 中配置视频列表")
            return

        logger.info(f"共有 {self.total_videos} 个视频待播放\n")

        for idx, href in enumerate(self.config.VIDEO_HREF_LIST, 1):
            if not self.session_active:
                logger.info("会话已停止，退出播放循环")
                break

            logger.info("=" * 60)
            logger.info(f"[{idx}/{self.total_videos}] 播放视频")
            logger.info(f"URL: {self.config.VIDEO_SITE_URL}{href}")
            logger.info("=" * 60)

            try:
                # 跳转到视频页面
                video_url = f"{self.config.VIDEO_SITE_URL.rstrip('/')}{href}"
                await self.page.goto(video_url, wait_until='domcontentloaded')
                await asyncio.sleep(2)

                # 播放视频
                await self._play_single_video()

                self.videos_completed += 1
                logger.info(f"✅ 视频 {idx} 播放完成\n")

            except Exception as e:
                logger.error(f"❌ 播放视频 {idx} 时出错: {e}")
                await self._save_screenshot(f"error_video_{idx}")

                # 询问是否继续
                try:
                    response = input(f"\n视频 {idx} 播放失败，是否继续下一个？(y/n): ").strip().lower()
                    if response != 'y':
                        logger.info("用户选择停止")
                        break
                except:
                    break

    async def _play_single_video(self):
        """播放单个视频的完整流程"""

        # 1. 等待视频播放器加载
        logger.info("等待视频播放器加载...")
        try:
            await self.page.wait_for_selector(
                self.config.VIDEO_PLAYER_SELECTOR,
                timeout=10000
            )
        except Exception as e:
            logger.warning(f"未找到视频播放器: {e}")
            await self._save_screenshot("no_video_player")
            return

        # 2. 尝试多种方式触发视频播放
        logger.info("点击视频触发播放...")
        play_success = False

        # 策略1: 点击 Plyr 播放按钮（覆盖层）
        try:
            plyr_button = await self.page.query_selector("button.plyr__control--overlaid, [data-plyr='play']")
            if plyr_button:
                is_visible = await plyr_button.is_visible()
                if is_visible:
                    logger.info("尝试点击 Plyr 播放按钮...")
                    await plyr_button.click()
                    await asyncio.sleep(self.config.PLAY_START_WAIT)
                    play_success = True
                    logger.info("✅ 通过 Plyr 按钮播放成功")
        except Exception as e:
            logger.debug(f"Plyr 按钮点击失败: {e}")

        # 策略2: 使用 JavaScript 直接播放
        if not play_success:
            try:
                logger.info("尝试使用 JavaScript 播放...")
                result = await self.page.evaluate(f"""
                    () => {{
                        const video = document.querySelector('{self.config.VIDEO_PLAYER_SELECTOR}');
                        if (video) {{
                            video.play();
                            return true;
                        }}
                        return false;
                    }}
                """)
                if result:
                    await asyncio.sleep(self.config.PLAY_START_WAIT)
                    play_success = True
                    logger.info("✅ 通过 JavaScript 播放成功")
            except Exception as e:
                logger.debug(f"JavaScript 播放失败: {e}")

        # 策略3: 强制点击视频元素
        if not play_success:
            try:
                logger.info("尝试强制点击视频元素...")
                await self.page.click(self.config.VIDEO_PLAYER_SELECTOR, force=True)
                await asyncio.sleep(self.config.PLAY_START_WAIT)
                play_success = True
                logger.info("✅ 通过强制点击播放成功")
            except Exception as e:
                logger.warning(f"所有播放方式均失败: {e}")

        if not play_success:
            logger.warning("⚠️ 无法触发视频播放，将继续监控状态...")

        # 3. 启动弹窗监控并等待视频完成
        logger.info("监控视频播放状态...")

        await asyncio.gather(
            self._monitor_and_handle_popups(),
            self._wait_for_video_complete(),
            return_exceptions=True
        )

    async def _monitor_and_handle_popups(self):
        """监控并处理弹窗"""
        while self.session_active:
            try:
                # 检查是否有"继续"按钮的弹窗
                continue_button = await self.page.query_selector(
                    self.config.CONTINUE_BUTTON_SELECTOR
                )

                if continue_button:
                    is_visible = await continue_button.is_visible()
                    if is_visible:
                        logger.info("🔔 检测到'继续'弹窗，正在点击...")
                        await continue_button.click()
                        await asyncio.sleep(1)
                        logger.info("✅ 已点击继续")

                await asyncio.sleep(self.config.POPUP_CHECK_INTERVAL)

            except Exception as e:
                logger.debug(f"弹窗监控异常: {e}")
                await asyncio.sleep(self.config.POPUP_CHECK_INTERVAL)

    async def _wait_for_video_complete(self):
        """等待视频播放完成"""
        start_time = datetime.now()
        check_interval = 5  # 每5秒检查一次

        while self.session_active:
            try:
                # 检查是否出现"播放完成"弹窗
                complete_popup = await self.page.query_selector(
                    self.config.COMPLETE_POPUP_SELECTOR
                )

                if complete_popup:
                    is_visible = await complete_popup.is_visible()
                    if is_visible:
                        logger.info("🎉 检测到'视频播放完成'弹窗")
                        logger.info(f"等待 {self.config.VIDEO_COMPLETE_WAIT} 秒后继续...")
                        await asyncio.sleep(self.config.VIDEO_COMPLETE_WAIT)
                        return  # 视频完成，退出等待

                # 检查视频播放状态（备用检测）
                video_status = await self.page.evaluate(f"""
                    () => {{
                        const video = document.querySelector('{self.config.VIDEO_PLAYER_SELECTOR}');
                        if (!video) return null;

                        return {{
                            currentTime: video.currentTime,
                            duration: video.duration,
                            ended: video.ended,
                            paused: video.paused,
                        }};
                    }}
                """)

                if video_status:
                    # 如果视频ended，也认为完成
                    if video_status.get('ended'):
                        logger.info("✅ 视频播放结束（通过video.ended检测）")
                        await asyncio.sleep(self.config.VIDEO_COMPLETE_WAIT)
                        return

                    # 定期输出播放进度
                    current = video_status.get('currentTime', 0)
                    duration = video_status.get('duration', 0)
                    if duration > 0:
                        progress = (current / duration) * 100
                        logger.debug(f"播放进度: {progress:.1f}% ({current:.0f}s / {duration:.0f}s)")

                # 检查超时
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > self.config.MAX_VIDEO_DURATION:
                    logger.warning(f"⏰ 视频播放超时 ({self.config.MAX_VIDEO_DURATION}秒)")
                    return

                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"等待视频完成时出错: {e}")
                await asyncio.sleep(check_interval)

    async def _save_screenshot(self, name: str):
        """保存截图"""
        if not self.config.SAVE_SCREENSHOTS or not self.page:
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = Path(self.config.SCREENSHOT_DIR) / f"{name}_{timestamp}.png"

            await self.page.screenshot(path=str(screenshot_path))
            logger.info(f"📸 截图已保存: {screenshot_path}")

        except Exception as e:
            logger.error(f"保存截图失败: {e}")

    async def _cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")

        self.session_active = False

        # 关闭浏览器
        if self.browser:
            await self.browser.close()

        logger.info("资源清理完成")


# 独立测试
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def test():
        automator = VideoAutomator()
        await automator.start()

    asyncio.run(test())
