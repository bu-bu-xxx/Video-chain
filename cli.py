#!/usr/bin/env python3
"""
Video Chain CLI - Command line interface for the video generation workflow
"""
import argparse
import sys
import os
from pathlib import Path
from video_chain import VideoChainWorkflow


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="视频链工作流 - 生成连贯的长视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python cli.py --description "一只猫在花园里玩耍，追逐蝴蝶，然后在树下睡觉"
  
  # 带参考图片
  python cli.py --description "机器人探索未来城市" --image robot.jpg
  
  # 自定义片段数和大小
  python cli.py --description "日出到日落的海滩景色" --segments 5 --size 1920x1080
        """
    )
    
    parser.add_argument(
        "--description", "-d",
        required=True,
        help="视频需求描述（中文）"
    )
    
    parser.add_argument(
        "--image", "-i",
        help="参考图片路径（可选）"
    )
    
    parser.add_argument(
        "--segments", "-s",
        type=int,
        default=3,
        help="视频片段数量（默认: 3）"
    )
    
    parser.add_argument(
        "--size",
        default="1280x720",
        choices=["1280x720", "720x1280", "1920x1080"],
        help="视频尺寸（默认: 1280x720）"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=4,
        help="每个片段的持续时间（秒）（默认: 4）"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="输出目录（默认: output）"
    )
    
    parser.add_argument(
        "--api-key",
        help="aihubmix API密钥（可选，也可通过AIHUBMIX_API_KEY环境变量设置）"
    )
    
    args = parser.parse_args()
    
    # Validate reference image if provided
    if args.image and not os.path.exists(args.image):
        print(f"错误: 参考图片不存在: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize workflow
        print("初始化视频链工作流...")
        workflow = VideoChainWorkflow(api_key=args.api_key)
        
        # Run the workflow
        final_video = workflow.run_workflow(
            user_description=args.description,
            reference_image_path=args.image,
            num_segments=args.segments,
            size=args.size,
            seconds_per_segment=args.duration,
            output_dir=args.output
        )
        
        if final_video:
            print(f"\n✓ 成功! 最终视频: {final_video}")
            sys.exit(0)
        else:
            print("\n✗ 失败: 无法生成视频", file=sys.stderr)
            sys.exit(1)
            
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        print("\n提示: 请设置AIHUBMIX_API_KEY环境变量或使用--api-key参数")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
