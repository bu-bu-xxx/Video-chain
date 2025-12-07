#!/usr/bin/env python3
"""
Installation verification script for Video Chain Workflow
"""

import sys
import os


def check_python_version():
    """Check Python version"""
    print("检查 Python 版本...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n检查依赖包...")
    
    packages = {
        'openai': 'OpenAI SDK',
        'requests': 'Requests',
        'dotenv': 'python-dotenv',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'flask': 'Flask',
        'moviepy.editor': 'MoviePy'
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (未安装)")
            all_installed = False
    
    return all_installed


def check_api_key():
    """Check if API key is configured"""
    print("\n检查 API 密钥配置...", end=" ")
    
    # Try loading from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    api_key = os.getenv('AIHUBMIX_API_KEY')
    
    if api_key:
        masked_key = api_key[:6] + '*' * (len(api_key) - 10) + api_key[-4:] if len(api_key) > 10 else '***'
        print(f"✓ 已设置 ({masked_key})")
        return True
    else:
        print("✗ 未设置")
        print("\n  请设置 AIHUBMIX_API_KEY 环境变量或创建 .env 文件")
        return False


def check_project_structure():
    """Check if project files exist"""
    print("\n检查项目文件...", end=" ")
    
    required_files = [
        'video_chain.py',
        'cli.py',
        'app.py',
        'requirements.txt',
        'templates/index.html'
    ]
    
    all_exist = True
    for file in required_files:
        if not os.path.exists(file):
            print(f"\n  ✗ 缺少文件: {file}")
            all_exist = False
    
    if all_exist:
        print("✓ 所有文件完整")
    
    return all_exist


def main():
    """Run all checks"""
    print("""
╔════════════════════════════════════════════════╗
║     Video Chain Workflow - 安装检查            ║
╚════════════════════════════════════════════════╝
    """)
    
    checks = [
        check_python_version(),
        check_project_structure(),
        check_dependencies(),
        check_api_key()
    ]
    
    print("\n" + "="*50)
    
    if all(checks):
        print("\n✓ 所有检查通过! 您可以开始使用了。")
        print("\n快速开始:")
        print("  命令行: python cli.py --description \"您的视频描述\"")
        print("  Web界面: python app.py")
        print("\n详细文档: README.md")
        return 0
    else:
        print("\n✗ 部分检查失败，请解决上述问题后再试。")
        print("\n安装依赖: pip install -r requirements.txt")
        print("配置API: cp .env.example .env 并编辑填入密钥")
        return 1


if __name__ == "__main__":
    sys.exit(main())
