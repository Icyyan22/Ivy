#!/usr/bin/env python3
"""
选择器测试工具
帮助您快速测试和验证网站的选择器配置
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def test_selectors():
    """测试选择器的交互式工具"""

    print("=" * 60)
    print("选择器测试工具")
    print("=" * 60)
    print()

    # 获取网站URL
    url = input("请输入视频网站URL: ").strip()
    if not url:
        print("❌ URL不能为空")
        return

    print(f"\n正在打开网站: {url}")
    print("(浏览器窗口会保持打开状态，方便您测试)\n")

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 访问网站
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')

            print("✅ 页面加载完成\n")

            # 交互式测试循环
            while True:
                print("-" * 60)
                print("请选择要测试的选择器类型：")
                print("  1. 视频列表 (VIDEO_LIST_SELECTOR)")
                print("  2. 视频播放器 (MAIN_VIDEO_SELECTOR)")
                print("  3. 下一个视频按钮 (NEXT_VIDEO_BUTTON_SELECTOR)")
                print("  4. 弹窗 (POPUP_SELECTORS)")
                print("  5. 弹窗关闭按钮 (POPUP_CLOSE_SELECTORS)")
                print("  6. 自定义选择器")
                print("  0. 退出")
                print("-" * 60)

                choice = input("请选择 (0-6): ").strip()

                if choice == "0":
                    break

                # 预设选择器
                preset_selectors = {
                    "1": [
                        ".video-list-item",
                        "[class*='video-item']",
                        "[class*='course-item']",
                        ".lesson-item"
                    ],
                    "2": [
                        "video",
                        ".video-player video",
                        "#video-player video",
                        "[class*='player'] video"
                    ],
                    "3": [
                        ".next-video",
                        "button:has-text('下一个')",
                        "[class*='next']",
                        ".btn-next"
                    ],
                    "4": [
                        ".popup",
                        ".modal",
                        "[role='dialog']",
                        "[class*='mask']"
                    ],
                    "5": [
                        "button:has-text('关闭')",
                        "button:has-text('确定')",
                        ".close-btn",
                        "[class*='close']"
                    ]
                }

                if choice in preset_selectors:
                    print(f"\n测试预设选择器:")
                    for selector in preset_selectors[choice]:
                        await test_single_selector(page, selector)

                elif choice == "6":
                    selector = input("\n请输入自定义选择器: ").strip()
                    if selector:
                        await test_single_selector(page, selector)

                print()

            print("\n感谢使用！")

        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

        finally:
            input("\n按回车键关闭浏览器...")
            await browser.close()


async def test_single_selector(page, selector: str):
    """
    测试单个选择器

    Args:
        page: Playwright Page 对象
        selector: CSS 选择器
    """
    try:
        # 查找所有匹配的元素
        elements = await page.query_selector_all(selector)
        count = len(elements)

        if count > 0:
            print(f"  ✅ {selector:<50} 找到 {count} 个元素")

            # 如果找到元素，高亮显示
            try:
                await page.evaluate(f"""
                    (selector) => {{
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {{
                            el.style.border = '3px solid red';
                            el.style.boxShadow = '0 0 10px red';
                        }});
                        setTimeout(() => {{
                            elements.forEach(el => {{
                                el.style.border = '';
                                el.style.boxShadow = '';
                            }});
                        }}, 2000);
                    }}
                """, selector)
                print(f"     (元素已高亮2秒)")
            except Exception:
                pass

        else:
            print(f"  ❌ {selector:<50} 未找到元素")

    except Exception as e:
        print(f"  ⚠️  {selector:<50} 出错: {e}")


async def quick_test(url: str):
    """
    快速测试所有常用选择器

    Args:
        url: 网站URL
    """
    print(f"正在测试: {url}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')

            print("测试结果:\n")

            # 测试视频列表
            print("📹 视频列表选择器:")
            for selector in [".video-item", "[class*='video']", ".course-item", ".lesson-item"]:
                await test_single_selector(page, selector)

            print("\n🎬 视频播放器选择器:")
            for selector in ["video", ".video-player video", "#video-player video"]:
                await test_single_selector(page, selector)

            print("\n⏭️ 下一个按钮选择器:")
            for selector in [".next-video", "button:has-text('下一个')", "[class*='next']"]:
                await test_single_selector(page, selector)

            print("\n🔔 弹窗选择器:")
            for selector in [".popup", ".modal", "[role='dialog']"]:
                await test_single_selector(page, selector)

            input("\n按回车键关闭...")
            await browser.close()

        except Exception as e:
            print(f"错误: {e}")
            await browser.close()


if __name__ == "__main__":
    print()

    if len(sys.argv) > 1:
        # 如果提供了URL参数，直接运行快速测试
        url = sys.argv[1]
        asyncio.run(quick_test(url))
    else:
        # 否则运行交互式测试
        asyncio.run(test_selectors())
