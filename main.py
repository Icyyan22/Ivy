#!/usr/bin/env python3
"""
视频学习网站自动化脚本 - 主程序入口 (简化版)
支持手动登录 + 自动播放视频列表
"""

import sys
import asyncio
import logging
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from video_automator import VideoAutomator


def setup_logging(verbose: bool = True):
    """
    配置日志系统

    Args:
        verbose: 是否输出详细日志
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%H:%M:%S'

    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # 输出到控制台
            logging.FileHandler(  # 输出到文件
                'video_automation.log',
                mode='a',
                encoding='utf-8'
            )
        ]
    )

    # 设置第三方库的日志级别（避免过多输出）
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          党课学习 v2.0                                     ║
    ║          Video Learning Automation Script                 ║
    ║                                                           ║
    ║          功能:                                             ║
    ║          • 手动登录（支持验证码）                             ║
    ║          • 自动播放视频列表                                  ║
    ║          • 自动处理"继续"弹窗                                ║
    ║          • 检测"播放完成"自动切换                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_disclaimer() -> bool:
    """
    打印免责声明并获取用户确认

    Returns:
        bool: 用户是否同意
    """
    disclaimer = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                    ⚠️  免责声明 / Disclaimer ⚠️            ║
    ║                                                           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║                                                           ║
    ║  本脚本仅供实在没有时间的太理学子使用，请在空闲时间认真学习         ║
    ║  This script is for learning and research purposes only.  ║
    ║                                                           ║
    ║  使用本脚本时请遵守：                                        ║
    ║  • 相关法律法规                                             ║
    ║  • 网站服务条款和使用协议                                     ║
    ║  • 学校/机构的相关规定                                        ║
    ║                                                            ║
    ║  用户需自行承担使用本脚本所产生的一切后果和责任。                 ║
    ║  开发者不对任何滥用行为负责。                                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(disclaimer)

    try:
        response = input("输入 'yes' 确认并继续，或输入其他内容退出: ").strip().lower()
        if response == 'yes':
            print("\n✅ 已确认免责声明\n")
            return True
        else:
            print("\n❌ 未确认免责声明，程序退出")
            return False
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
        return False


def print_config_info(config: Config):
    """打印配置信息"""
    print("\n当前配置:")
    print(f"  基础URL: {config.VIDEO_SITE_URL}")
    print(f"  视频数量: {len(config.VIDEO_HREF_LIST)}")
    print(f"  无头模式: {config.HEADLESS}")
    print(f"  详细日志: {config.VERBOSE_LOGGING}")
    print()


def check_config(config: Config) -> bool:
    """
    检查配置是否有效

    Args:
        config: 配置对象

    Returns:
        bool: 配置是否有效
    """
    if not config.VIDEO_SITE_URL or config.VIDEO_SITE_URL == "https://your-video-site.com/":
        print("\n⚠️  警告: 请先修改 config.py 中的 VIDEO_SITE_URL 配置！")
        print("   请将其修改为实际的视频学习网站URL\n")
        return False

    if not config.VIDEO_HREF_LIST:
        print("\n⚠️  警告: VIDEO_HREF_LIST 为空！")
        print("   请在 config.py 中配置要播放的视频列表")
        print("\n   示例:")
        print("   VIDEO_HREF_LIST = [")
        print("       '/course/video/1',")
        print("       '/course/video/2',")
        print("   ]")
        print()

        response = input("是否继续（用于测试）？(y/n): ").strip().lower()
        if response != 'y':
            return False

    return True


def print_usage_tips():
    """打印使用提示"""
    print("\n使用流程:")
    print("  1. 脚本会打开浏览器并跳转到登录页面")
    print("  2. 您需要手动完成登录（包括验证码）")
    print("  3. 登录成功后，回到命令行按回车继续")
    print("  4. 脚本会自动依次播放配置的视频列表")
    print("  5. 遇到'继续'弹窗会自动点击")
    print("  6. 检测到'播放完成'后自动跳转下一个")
    print("  7. 按 Ctrl+C 可以随时中断")
    print()


async def main():
    """主函数"""
    # 打印启动横幅
    print_banner()

    # 显示免责声明并获取确认
    if not print_disclaimer():
        return

    # 加载配置
    config = Config()

    # 配置日志
    setup_logging(verbose=config.VERBOSE_LOGGING)

    logger = logging.getLogger(__name__)
    logger.info("视频自动化脚本启动...")

    # 打印配置信息
    print_config_info(config)

    # 检查配置
    if not check_config(config):
        print_usage_tips()
        return

    # 打印使用提示
    print_usage_tips()

    # 确认开始
    try:
        print("准备启动浏览器...")
        response = input("按回车开始，或输入 'q' 退出: ").strip().lower()
        if response == 'q':
            print("已取消")
            return
    except KeyboardInterrupt:
        print("\n已取消")
        return

    print("\n正在启动浏览器...\n")

    # 创建并启动自动化器
    try:
        automator = VideoAutomator(config)
        await automator.start()

        print("\n✅ 自动化完成！")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        logger.info("用户手动中断脚本")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        logger.error(f"脚本运行出错: {e}", exc_info=True)

    finally:
        print("\n感谢使用！\n")


if __name__ == "__main__":
    try:
        # 运行主函数
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n\n程序已退出")

    except Exception as e:
        print(f"\n严重错误: {e}")
        sys.exit(1)
