#!/usr/bin/env python3
"""
Basic validation tests that can run without installing dependencies.

These tests validate:
- Python syntax
- File structure
- Import structure (without actually importing)
- Configuration files
"""
import os
import sys
import ast


def test_python_syntax():
    """Test that all Python files have valid syntax"""
    print("Testing Python syntax...")
    
    python_files = [
        'video_chain.py',
        'cli.py',
        'app.py',
        'example.py',
        'check_setup.py'
    ]
    
    errors = []
    for filename in python_files:
        if not os.path.exists(filename):
            errors.append(f"File not found: {filename}")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
                ast.parse(source)
            print(f"  ✅ {filename}")
        except SyntaxError as e:
            errors.append(f"{filename}: {e}")
            print(f"  ❌ {filename}: {e}")
    
    return len(errors) == 0, errors


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'video_chain.py',
        'cli.py',
        'app.py',
        'example.py',
        'check_setup.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'TESTING.md',
        'LICENSE',
        '.env.example',
        '.gitignore',
        'templates/index.html'
    ]
    
    missing = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✅ {filename}")
        else:
            missing.append(filename)
            print(f"  ❌ {filename} (missing)")
    
    return len(missing) == 0, missing


def test_imports_structure():
    """Test that import statements are properly structured"""
    print("\nTesting import structure...")
    
    test_cases = [
        ('video_chain.py', ['OpenAI', 'requests', 'cv2', 'PIL']),
        ('app.py', ['Flask', 'VideoChainWorkflow']),
        ('cli.py', ['argparse', 'VideoChainWorkflow']),
    ]
    
    errors = []
    for filename, expected_imports in test_cases:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source)
            
            # Extract import names
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                    for alias in node.names:
                        imports.append(alias.name)
            
            # Check if expected imports are present
            for expected in expected_imports:
                if expected in source:  # Simple string check
                    print(f"  ✅ {filename}: has {expected}")
                else:
                    errors.append(f"{filename}: missing import {expected}")
                    print(f"  ❌ {filename}: missing {expected}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            print(f"  ❌ {filename}: {e}")
    
    return len(errors) == 0, errors


def test_documentation():
    """Test that documentation is comprehensive"""
    print("\nTesting documentation...")
    
    doc_files = {
        'README.md': 3000,  # At least 3KB
        'QUICKSTART.md': 500,  # At least 500 bytes
        'TESTING.md': 1000,  # At least 1KB
    }
    
    errors = []
    for filename, min_size in doc_files.items():
        if not os.path.exists(filename):
            errors.append(f"{filename} not found")
            print(f"  ❌ {filename} (not found)")
            continue
        
        size = os.path.getsize(filename)
        if size >= min_size:
            print(f"  ✅ {filename} ({size} bytes)")
        else:
            errors.append(f"{filename} too small ({size} < {min_size})")
            print(f"  ❌ {filename} ({size} bytes < {min_size} bytes)")
    
    return len(errors) == 0, errors


def test_configuration_files():
    """Test that configuration files are properly set up"""
    print("\nTesting configuration files...")
    
    errors = []
    
    # Test .env.example
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'AIHUBMIX_API_KEY' in content:
                print("  ✅ .env.example has API key placeholder")
            else:
                errors.append(".env.example missing API key placeholder")
                print("  ❌ .env.example missing API key placeholder")
    else:
        errors.append(".env.example not found")
        print("  ❌ .env.example not found")
    
    # Test requirements.txt
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = ['openai', 'requests', 'flask', 'opencv-python', 'moviepy']
            for package in required_packages:
                if package in content:
                    print(f"  ✅ requirements.txt includes {package}")
                else:
                    errors.append(f"requirements.txt missing {package}")
                    print(f"  ❌ requirements.txt missing {package}")
    else:
        errors.append("requirements.txt not found")
        print("  ❌ requirements.txt not found")
    
    return len(errors) == 0, errors


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Video Chain Workflow - Basic Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Python Syntax", test_python_syntax),
        ("File Structure", test_file_structure),
        ("Import Structure", test_imports_structure),
        ("Documentation", test_documentation),
        ("Configuration Files", test_configuration_files),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        passed, errors = test_func()
        results.append((test_name, passed, errors))
        if not passed:
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed, errors in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed and errors:
            for error in errors:
                print(f"  - {error}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All validation tests passed!")
        print("\nNote: These are basic validation tests.")
        print("Full functional tests require:")
        print("  1. pip install -r requirements.txt")
        print("  2. Valid AIHUBMIX_API_KEY")
        print("  3. python test_video_chain.py (unit tests)")
        return 0
    else:
        print("\n❌ Some validation tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
