# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 配置API密钥

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入您的API密钥
# AIHUBMIX_API_KEY=sk-your-api-key-here
```

或者直接设置环境变量：

```bash
export AIHUBMIX_API_KEY=sk-your-api-key-here
```

## 3. 运行示例

### 方式一：命令行 (CLI)

```bash
python cli.py --description "一只可爱的小猫在花园里玩耍"
```

### 方式二：Web界面

```bash
python app.py
```

然后在浏览器打开 http://localhost:5000

### 方式三：Python脚本

```bash
python example.py
```

## 4. 查看结果

生成的视频默认保存在 `output/` 目录下。

## 常见问题

### Q: 如何获取API密钥？

A: 访问 https://aihubmix.com 注册账号并获取API密钥。

### Q: 生成需要多长时间？

A: 每个视频片段大约需要30秒到2分钟，具体时间取决于API服务器负载。

### Q: 支持哪些视频尺寸？

A: 
- 1280x720 (横屏 16:9)
- 720x1280 (竖屏 9:16)  
- 1920x1080 (全高清)

### Q: 可以生成多长的视频？

A: 每个片段2-10秒，建议3-5个片段，总长度12-50秒。

## 更多示例

查看 `example.py` 文件获取更多编程示例。

查看 `README.md` 获取完整文档。
