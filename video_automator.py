"""
视频自动化核心模块 - 简化版
支持手动登录 + 自动播放视频列表
"""

import asyncio
import logging
import os
import requests
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

                # 步骤1: 登录（根据配置选择自动或手动）
                if self.config.AUTO_LOGIN_ENABLED and self._validate_auto_login_config():
                    await self._auto_login_flow()
                else:
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

                # 处理进入视频页面时的弹窗（如"我知道了"按钮）
                await self._handle_entry_popup()

                # 播放视频
                await self._play_single_video()

                self.videos_completed += 1
                logger.info(f"✅ 视频 {idx} 播放完成\n")

                # 每个视频播放完成后重新登录（避免超时）
                if self.config.AUTO_LOGIN_ENABLED and idx < self.total_videos:
                    logger.info("重新登录以避免超时...")
                    await self._auto_login_flow()

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

    async def _handle_entry_popup(self):
        """处理进入视频页面时的弹窗（如"我知道了"按钮）"""
        logger.info("检查进入视频页面时的弹窗...")

        try:
            # 遍历所有可能的关闭按钮选择器
            for selector in self.config.POPUP_CLOSE_SELECTORS:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        is_visible = await button.is_visible()
                        if is_visible:
                            logger.info(f"检测到弹窗按钮: {selector}，正在点击...")
                            await button.click()
                            await asyncio.sleep(1)
                            logger.info("✅ 已点击弹窗按钮")
                            return True
                except Exception as e:
                    logger.debug(f"检查按钮 {selector} 时出错: {e}")
                    continue

            logger.debug("未检测到进入页面时的弹窗")
            return False

        except Exception as e:
            logger.debug(f"处理进入页面弹窗时出错: {e}")
            return False

    async def _handle_completion_popup(self):
        """处理视频播放完成后的弹窗（如"我知道了"按钮）"""
        logger.info("检查视频完成后的弹窗...")

        try:
            # 遍历所有可能的关闭按钮选择器
            for selector in self.config.POPUP_CLOSE_SELECTORS:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        is_visible = await button.is_visible()
                        if is_visible:
                            logger.info(f"检测到完成弹窗按钮: {selector}，正在点击...")
                            await button.click()
                            await asyncio.sleep(1)
                            logger.info("✅ 已点击完成弹窗按钮")
                            return True
                except Exception as e:
                    logger.debug(f"检查按钮 {selector} 时出错: {e}")
                    continue

            logger.debug("未检测到完成弹窗按钮")
            return False

        except Exception as e:
            logger.debug(f"处理完成弹窗时出错: {e}")
            return False

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
        logger.info(f"开始监控弹窗 (检测间隔: {self.config.POPUP_CHECK_INTERVAL}秒)")

        while self.session_active:
            try:
                # 遍历所有可能的"继续"按钮选择器
                for selector in self.config.CONTINUE_BUTTON_SELECTORS:
                    try:
                        continue_button = await self.page.query_selector(selector)

                        if continue_button:
                            is_visible = await continue_button.is_visible()
                            if is_visible:
                                # 获取按钮文本以便日志输出
                                button_text = await continue_button.text_content()
                                logger.info(f"🔔 检测到弹窗按钮: '{button_text.strip()}' (选择器: {selector})")
                                logger.info("正在点击...")
                                await continue_button.click()
                                await asyncio.sleep(1)
                                logger.info("✅ 已点击弹窗按钮")
                                break  # 找到并点击后退出循环
                    except Exception as e:
                        logger.debug(f"检查选择器 {selector} 时出错: {e}")
                        continue

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

                        # 处理完成后的弹窗按钮（如"我知道了"）
                        await self._handle_completion_popup()

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

                        # 处理完成后的弹窗按钮（如"我知道了"）
                        await self._handle_completion_popup()

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

    # ===== 自动登录相关方法 =====

    def _validate_auto_login_config(self) -> bool:
        """验证自动登录配置是否完整"""
        if not self.config.AUTO_LOGIN_ENABLED:
            return False

        missing = []
        if not self.config.LOGIN_USERNAME:
            missing.append("LOGIN_USERNAME")
        if not self.config.LOGIN_PASSWORD:
            missing.append("LOGIN_PASSWORD")
        if not self.config.CAPTCHA_API_KEY:
            missing.append("CAPTCHA_API_KEY")
        if not self.config.CAPTCHA_API_BASE_URL:
            missing.append("CAPTCHA_API_BASE_URL")

        if missing:
            logger.warning(f"自动登录配置不完整，缺少: {', '.join(missing)}")
            logger.warning("请在 config.py 中填写相关配置")
            return False

        return True

    async def _recognize_captcha(self) -> Optional[str]:
        """
        从验证码图片元素获取 URL 并使用 HTTP API 识别验证码

        Returns:
            str: 识别出的验证码文本，失败返回 None
        """
        try:
            logger.info("正在获取验证码图片 URL...")

            # 定位验证码图片元素
            captcha_img = self.page.locator(f"xpath={self.config.LOGIN_CAPTCHA_IMAGE_XPATH}")

            # 等待元素可见
            await captcha_img.wait_for(state="visible", timeout=5000)

            # 获取图片的 src 属性
            captcha_url = await captcha_img.get_attribute("src")
            if not captcha_url:
                logger.error("无法获取验证码图片 URL")
                return None

            logger.info(f"验证码图片 URL: {captcha_url}")

            # 调用 API 识别验证码
            logger.info("正在调用 API 识别验证码...")

            # 构建请求体
            payload = {
                "model": self.config.CAPTCHA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.config.CAPTCHA_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": captcha_url
                                }
                            }
                        ]
                    }
                ]
            }

            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.config.CAPTCHA_API_KEY}"
            }

            # 发送 POST 请求
            response = requests.post(
                self.config.CAPTCHA_API_BASE_URL,
                json=payload,
                headers=headers,
                timeout=30
            )

            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"API 请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return None

            # 解析响应
            response_data = response.json()
            captcha_text = response_data["choices"][0]["message"]["content"].strip()

            logger.info(f"✅ 验证码识别结果: {captcha_text}")
            return captcha_text

        except Exception as e:
            logger.error(f"验证码识别失败: {e}")
            return None


    async def _auto_login_flow(self) -> bool:
        """
        自动登录流程

        Returns:
            bool: 登录是否成功
        """
        logger.info("\n" + "=" * 60)
        logger.info("开始自动登录流程")
        logger.info("=" * 60)

        # 验证配置
        if not self._validate_auto_login_config():
            logger.warning("自动登录配置不完整，降级为手动登录")
            await self._manual_login_flow()
            return True

        # 导航到登录页面
        try:
            logger.info(f"正在打开登录页面: {self.config.VIDEO_SITE_URL}")
            await self.page.goto(self.config.VIDEO_SITE_URL, wait_until='domcontentloaded')
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"打开登录页面失败: {e}")
            return False

        # 重试登录
        for attempt in range(1, self.config.CAPTCHA_MAX_RETRIES + 1):
            try:
                logger.info(f"登录尝试 {attempt}/{self.config.CAPTCHA_MAX_RETRIES}")

                # 1. 填写用户名
                logger.info("填写用户名...")
                username_input = self.page.locator(f"xpath={self.config.LOGIN_USERNAME_XPATH}")
                await username_input.wait_for(state="visible", timeout=10000)
                await username_input.clear()
                await username_input.fill(self.config.LOGIN_USERNAME)

                # 2. 填写密码
                logger.info("填写密码...")
                password_input = self.page.locator(f"xpath={self.config.LOGIN_PASSWORD_XPATH}")
                await password_input.clear()
                await password_input.fill(self.config.LOGIN_PASSWORD)

                # 3. 识别验证码
                captcha_text = await self._recognize_captcha()
                if not captcha_text:
                    logger.warning(f"识别验证码失败，尝试 {attempt + 1}")
                    await asyncio.sleep(2)
                    continue

                # 4. 填写验证码
                logger.info(f"填写验证码: {captcha_text}")
                captcha_input = self.page.locator(f"xpath={self.config.LOGIN_CAPTCHA_INPUT_XPATH}")
                await captcha_input.clear()
                await captcha_input.fill(captcha_text)

                # 5. 点击登录按钮
                logger.info("点击登录按钮...")
                login_button = self.page.locator(f"xpath={self.config.LOGIN_SUBMIT_BUTTON_XPATH}")
                await login_button.click()

                # 6. 等待登录结果
                await asyncio.sleep(self.config.LOGIN_WAIT_AFTER_SUBMIT)

                # 7. 检查是否登录成功（简单检查：URL是否变化或者不在登录页）
                current_url = self.page.url
                if self.config.VIDEO_SITE_URL not in current_url or "login" not in current_url.lower():
                    logger.info("✅ 自动登录成功！")
                    return True
                else:
                    logger.warning(f"登录可能失败（仍在登录页），尝试 {attempt + 1}")
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"登录尝试 {attempt} 出错: {e}")
                await asyncio.sleep(2)

        # 所有尝试都失败
        logger.error(f"❌ 自动登录失败（{self.config.CAPTCHA_MAX_RETRIES} 次尝试）")
        logger.info("降级为手动登录...")
        await self._manual_login_flow()
        return False


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
