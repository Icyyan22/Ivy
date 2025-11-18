"""
窗口管理模块
负责保持浏览器窗口在最前面，并监测窗口焦点
支持 macOS, Windows, Linux
"""

import asyncio
import platform
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WindowManager:
    """窗口管理器 - 保持窗口在最上层"""

    def __init__(self):
        self.system = platform.system()
        self.monitoring = False
        logger.info(f"窗口管理器初始化 - 操作系统: {self.system}")

    async def keep_window_on_top(self, window_title: str = "Chromium"):
        """
        保持窗口在最前面

        Args:
            window_title: 窗口标题关键词
        """
        try:
            if self.system == "Darwin":  # macOS
                self._keep_window_on_top_macos(window_title)
            elif self.system == "Windows":
                self._keep_window_on_top_windows(window_title)
            elif self.system == "Linux":
                self._keep_window_on_top_linux(window_title)
            else:
                logger.warning(f"不支持的操作系统: {self.system}")
        except Exception as e:
            logger.error(f"设置窗口置顶失败: {e}")

    def _keep_window_on_top_macos(self, window_title: str):
        """macOS: 使用 AppleScript 将窗口置顶"""
        import subprocess

        # 方案1: 激活应用程序到前台
        script = f"""
        tell application "System Events"
            set frontmost of first process whose name contains "{window_title}" to true
        end tell
        """
        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"macOS: 成功将 {window_title} 窗口置顶")
        except subprocess.CalledProcessError as e:
            logger.error(f"macOS: AppleScript 执行失败: {e.stderr}")

        # 方案2: 使用 Quartz (更底层的API)
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            from AppKit import NSWorkspace

            # 激活包含指定标题的应用
            workspace = NSWorkspace.sharedWorkspace()
            for app in workspace.runningApplications():
                if window_title.lower() in app.localizedName().lower():
                    app.activateWithOptions_(1 << 1)  # NSApplicationActivateIgnoringOtherApps
                    logger.debug(f"macOS: 使用 AppKit 激活应用 {app.localizedName()}")
                    break

        except ImportError:
            logger.warning("macOS: 未安装 pyobjc，仅使用 AppleScript 方式")
        except Exception as e:
            logger.error(f"macOS: Quartz 方式失败: {e}")

    def _keep_window_on_top_windows(self, window_title: str):
        """Windows: 使用 Win32 API 将窗口置顶"""
        try:
            import win32gui
            import win32con

            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        windows.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if windows:
                hwnd = windows[0]
                # 设置为最顶层窗口
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                logger.debug(f"Windows: 成功将窗口 {hwnd} 置顶")
            else:
                logger.warning(f"Windows: 未找到包含 '{window_title}' 的窗口")

        except ImportError:
            logger.error("Windows: 未安装 pywin32，无法使用窗口管理功能")
        except Exception as e:
            logger.error(f"Windows: 设置窗口置顶失败: {e}")

    def _keep_window_on_top_linux(self, window_title: str):
        """Linux: 使用 wmctrl 将窗口置顶"""
        import subprocess

        try:
            # 需要安装 wmctrl: sudo apt-get install wmctrl
            subprocess.run(
                ["wmctrl", "-r", window_title, "-b", "add,above"],
                check=True,
                capture_output=True
            )
            logger.debug(f"Linux: 成功将 {window_title} 窗口置顶")
        except FileNotFoundError:
            logger.error("Linux: 未安装 wmctrl，请运行: sudo apt-get install wmctrl")
        except subprocess.CalledProcessError as e:
            logger.error(f"Linux: wmctrl 执行失败: {e}")

    async def check_window_focused(self, window_title: str = "Chromium") -> bool:
        """
        检查窗口是否获得焦点

        Args:
            window_title: 窗口标题关键词

        Returns:
            bool: 窗口是否在前台
        """
        try:
            if self.system == "Darwin":
                return self._check_window_focused_macos(window_title)
            elif self.system == "Windows":
                return self._check_window_focused_windows(window_title)
            elif self.system == "Linux":
                return self._check_window_focused_linux(window_title)
            else:
                return True  # 不支持的系统默认返回 True
        except Exception as e:
            logger.error(f"检查窗口焦点失败: {e}")
            return True

    def _check_window_focused_macos(self, window_title: str) -> bool:
        """macOS: 检查窗口是否在前台"""
        import subprocess

        script = """
        tell application "System Events"
            return name of first application process whose frontmost is true
        end tell
        """
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            frontmost_app = result.stdout.strip()
            is_focused = window_title.lower() in frontmost_app.lower()
            logger.debug(f"macOS: 前台应用: {frontmost_app}, 目标: {window_title}, 匹配: {is_focused}")
            return is_focused
        except Exception as e:
            logger.error(f"macOS: 检查窗口焦点失败: {e}")
            return True

    def _check_window_focused_windows(self, window_title: str) -> bool:
        """Windows: 检查窗口是否在前台"""
        try:
            import win32gui

            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            is_focused = window_title.lower() in title.lower()
            logger.debug(f"Windows: 前台窗口: {title}, 目标: {window_title}, 匹配: {is_focused}")
            return is_focused
        except Exception as e:
            logger.error(f"Windows: 检查窗口焦点失败: {e}")
            return True

    def _check_window_focused_linux(self, window_title: str) -> bool:
        """Linux: 检查窗口是否在前台"""
        import subprocess

        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True,
                text=True,
                check=True
            )
            active_window = result.stdout.strip()
            is_focused = window_title.lower() in active_window.lower()
            logger.debug(f"Linux: 前台窗口: {active_window}, 目标: {window_title}, 匹配: {is_focused}")
            return is_focused
        except FileNotFoundError:
            logger.warning("Linux: 未安装 xdotool，无法检查窗口焦点")
            return True
        except Exception as e:
            logger.error(f"Linux: 检查窗口焦点失败: {e}")
            return True

    async def monitor_and_maintain_focus(
        self,
        page,
        check_interval: int = 3,
        window_title: str = "Chromium"
    ):
        """
        持续监测并维护窗口焦点

        Args:
            page: Playwright Page 对象
            check_interval: 检测间隔(秒)
            window_title: 窗口标题关键词
        """
        self.monitoring = True
        logger.info(f"开始监测窗口焦点 (间隔: {check_interval}秒)")

        while self.monitoring:
            try:
                is_focused = await self.check_window_focused(window_title)

                if not is_focused:
                    logger.warning("窗口失去焦点，正在恢复...")
                    # 重新激活窗口
                    await self.keep_window_on_top(window_title)
                    await asyncio.sleep(0.5)

                    # 点击页面body恢复焦点
                    try:
                        await page.click("body", timeout=2000)
                        logger.info("已点击页面恢复焦点")
                    except Exception as e:
                        logger.debug(f"点击页面失败（可能不重要）: {e}")

                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"监测窗口焦点时出错: {e}")
                await asyncio.sleep(check_interval)

    def stop_monitoring(self):
        """停止窗口焦点监测"""
        self.monitoring = False
        logger.info("窗口焦点监测已停止")


# 独立测试
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def test():
        manager = WindowManager()
        print(f"当前操作系统: {manager.system}")

        # 测试窗口置顶
        await manager.keep_window_on_top("Chrome")

        # 测试检查焦点
        is_focused = await manager.check_window_focused("Chrome")
        print(f"Chrome窗口是否在前台: {is_focused}")

    asyncio.run(test())
