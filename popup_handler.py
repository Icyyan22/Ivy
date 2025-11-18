"""
弹窗处理模块
负责检测和处理页面中的弹窗（确认、继续等类型）
"""

import asyncio
import logging
from typing import List, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class PopupHandler:
    """弹窗处理器 - 自动检测并关闭弹窗"""

    def __init__(self, config):
        """
        初始化弹窗处理器

        Args:
            config: 配置对象，包含弹窗选择器等信息
        """
        self.config = config
        self.monitoring = False
        self.popup_count = 0
        logger.info("弹窗处理器初始化完成")

    async def detect_popup(self, page: Page) -> Optional[any]:
        """
        检测页面中是否存在弹窗

        Args:
            page: Playwright Page 对象

        Returns:
            弹窗元素，如果没有则返回 None
        """
        try:
            # 遍历所有可能的弹窗选择器
            for selector in self.config.POPUP_SELECTORS:
                try:
                    popup = await page.query_selector(selector)
                    if popup:
                        # 检查弹窗是否可见
                        is_visible = await popup.is_visible()
                        if is_visible:
                            logger.debug(f"检测到弹窗: {selector}")
                            return popup
                except Exception as e:
                    logger.debug(f"检查选择器 {selector} 时出错: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"检测弹窗时出错: {e}")
            return None

    async def find_close_button(self, page: Page) -> Optional[any]:
        """
        查找弹窗的关闭/确认按钮

        Args:
            page: Playwright Page 对象

        Returns:
            按钮元素，如果没有则返回 None
        """
        try:
            # 遍历所有可能的关闭按钮选择器
            for selector in self.config.POPUP_CLOSE_SELECTORS:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        is_visible = await button.is_visible()
                        if is_visible:
                            logger.debug(f"找到关闭按钮: {selector}")
                            return button
                except Exception as e:
                    logger.debug(f"检查按钮选择器 {selector} 时出错: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"查找关闭按钮时出错: {e}")
            return None

    async def close_popup(self, page: Page) -> bool:
        """
        尝试关闭弹窗

        Args:
            page: Playwright Page 对象

        Returns:
            bool: 是否成功关闭弹窗
        """
        try:
            # 策略1: 查找并点击关闭按钮
            close_button = await self.find_close_button(page)
            if close_button:
                logger.info("点击关闭按钮...")
                await close_button.click()
                await asyncio.sleep(0.5)
                self.popup_count += 1
                logger.info(f"成功关闭弹窗 (累计: {self.popup_count})")
                return True

            # 策略2: 尝试按 ESC 键关闭
            logger.debug("尝试按 ESC 键关闭弹窗...")
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.5)

            # 验证弹窗是否还在
            popup_still_exists = await self.detect_popup(page)
            if not popup_still_exists:
                self.popup_count += 1
                logger.info(f"通过 ESC 键关闭弹窗 (累计: {self.popup_count})")
                return True

            # 策略3: 点击弹窗外部（遮罩层）
            logger.debug("尝试点击遮罩层关闭弹窗...")
            overlay_selectors = [
                ".modal-backdrop",
                ".overlay",
                "[class*='mask']",
                "[class*='backdrop']"
            ]

            for selector in overlay_selectors:
                try:
                    overlay = await page.query_selector(selector)
                    if overlay:
                        await overlay.click()
                        await asyncio.sleep(0.5)

                        # 验证弹窗是否关闭
                        popup_still_exists = await self.detect_popup(page)
                        if not popup_still_exists:
                            self.popup_count += 1
                            logger.info(f"通过点击遮罩关闭弹窗 (累计: {self.popup_count})")
                            return True
                except Exception:
                    continue

            logger.warning("所有关闭弹窗的策略都失败了")
            return False

        except Exception as e:
            logger.error(f"关闭弹窗时出错: {e}")
            return False

    async def handle_popup(self, page: Page) -> bool:
        """
        检测并处理弹窗（完整流程）

        Args:
            page: Playwright Page 对象

        Returns:
            bool: 是否检测到并成功处理了弹窗
        """
        try:
            popup = await self.detect_popup(page)

            if popup:
                logger.info("检测到弹窗，正在处理...")
                success = await self.close_popup(page)
                return success
            else:
                return False

        except Exception as e:
            logger.error(f"处理弹窗时出错: {e}")
            return False

    async def monitor_popups(
        self,
        page: Page,
        check_interval: int = 2
    ):
        """
        持续监测并自动处理弹窗

        Args:
            page: Playwright Page 对象
            check_interval: 检测间隔(秒)
        """
        self.monitoring = True
        logger.info(f"开始监测弹窗 (间隔: {check_interval}秒)")

        while self.monitoring:
            try:
                await self.handle_popup(page)
                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"监测弹窗时出错: {e}")
                await asyncio.sleep(check_interval)

    def stop_monitoring(self):
        """停止弹窗监测"""
        self.monitoring = False
        logger.info(f"弹窗监测已停止 (累计处理: {self.popup_count} 个弹窗)")

    async def wait_and_handle_popup(
        self,
        page: Page,
        timeout: int = 5
    ) -> bool:
        """
        等待弹窗出现并处理（用于预期会出现弹窗的场景）

        Args:
            page: Playwright Page 对象
            timeout: 等待超时时间(秒)

        Returns:
            bool: 是否成功处理了弹窗
        """
        logger.info(f"等待弹窗出现 (超时: {timeout}秒)...")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            popup = await self.detect_popup(page)
            if popup:
                logger.info("弹窗已出现，正在处理...")
                success = await self.close_popup(page)
                return success

            await asyncio.sleep(0.5)

        logger.debug("在超时时间内未检测到弹窗")
        return False

    def get_statistics(self) -> dict:
        """
        获取弹窗处理统计信息

        Returns:
            dict: 统计信息
        """
        return {
            "total_popups_handled": self.popup_count,
            "is_monitoring": self.monitoring
        }


# 独立测试
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建测试配置
    class TestConfig:
        POPUP_SELECTORS = [".popup", ".modal", "[role='dialog']"]
        POPUP_CLOSE_SELECTORS = ["button:has-text('关闭')", ".close-btn"]

    async def test():
        from playwright.async_api import async_playwright

        config = TestConfig()
        handler = PopupHandler(config)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # 访问一个测试页面
            await page.goto("https://example.com")

            # 测试弹窗检测
            popup = await handler.detect_popup(page)
            print(f"检测到弹窗: {popup is not None}")

            # 获取统计信息
            stats = handler.get_statistics()
            print(f"统计信息: {stats}")

            await browser.close()

    asyncio.run(test())
