#!/usr/bin/env python3
"""
Example usage of the Video Chain Workflow

This script demonstrates how to use the VideoChainWorkflow class programmatically.
"""

from video_chain import VideoChainWorkflow


def example_basic():
    """Basic example without reference image"""
    print("=== 基本用法示例 ===\n")
    
    # Initialize workflow
    workflow = VideoChainWorkflow()
    
    # Run the workflow
    final_video = workflow.run_workflow(
        user_description="一只小猫在花园里玩耍，追逐蝴蝶，然后在树下休息",
        num_segments=3,
        size="1280x720",
        seconds_per_segment=4,
        output_dir="output/example1"
    )
    
    if final_video:
        print(f"\n✓ 成功! 视频已保存到: {final_video}")
    else:
        print("\n✗ 视频生成失败")


def example_with_image():
    """Example with reference image"""
    print("=== 带参考图片示例 ===\n")
    
    workflow = VideoChainWorkflow()
    
    final_video = workflow.run_workflow(
        user_description="机器人在未来城市中探索，观察周围的高科技建筑",
        reference_image_path="robot.jpg",  # 请替换为实际图片路径
        num_segments=3,
        size="1280x720",
        seconds_per_segment=5,
        output_dir="output/example2"
    )
    
    if final_video:
        print(f"\n✓ 成功! 视频已保存到: {final_video}")
    else:
        print("\n✗ 视频生成失败")


def example_custom_config():
    """Example with custom configuration"""
    print("=== 自定义配置示例 ===\n")
    
    workflow = VideoChainWorkflow()
    
    final_video = workflow.run_workflow(
        user_description="日出到日落的海滩美景，从黎明到黄昏的变化",
        num_segments=5,
        size="1920x1080",
        seconds_per_segment=6,
        output_dir="output/example3"
    )
    
    if final_video:
        print(f"\n✓ 成功! 视频已保存到: {final_video}")
    else:
        print("\n✗ 视频生成失败")


if __name__ == "__main__":
    import sys
    
    print("""
╔════════════════════════════════════════════════╗
║      Video Chain Workflow - 使用示例           ║
╚════════════════════════════════════════════════╝

请确保已设置 AIHUBMIX_API_KEY 环境变量
    """)
    
    print("选择示例:")
    print("1. 基本用法（无参考图片）")
    print("2. 带参考图片")
    print("3. 自定义配置")
    print("q. 退出")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == "1":
        example_basic()
    elif choice == "2":
        example_with_image()
    elif choice == "3":
        example_custom_config()
    elif choice.lower() == "q":
        print("退出")
        sys.exit(0)
    else:
        print("无效选项")
        sys.exit(1)
