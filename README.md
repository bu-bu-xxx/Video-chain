# 视频链工作流 (Video Chain Workflow)

一个基于AI的连贯视频生成系统，通过Sora-2和Gemini-3-pro-preview模型，根据用户描述自动生成多个连贯的视频片段并拼接成长视频。

## 功能特点

- 🎬 **智能分镜**: 使用Gemini-3-pro-preview自动生成每个视频片段的详细提示词
- 🔗 **连贯生成**: 使用前一个视频的最后一帧作为参考，确保视频片段之间的连贯性
- 🎨 **灵活配置**: 支持自定义片段数量、视频尺寸、时长等参数
- 🖼️ **参考图片**: 支持上传初始参考图片，引导视频风格
- 💻 **双模式**: 提供命令行和Web界面两种使用方式
- 🇨🇳 **中文优化**: 所有提示词和界面都使用中文

## 系统架构

```
用户输入 (图片+文字描述)
    ↓
Gemini-3-pro-preview 生成分镜提示词
    ↓
Sora-2 生成第一个视频片段
    ↓
提取最后一帧作为参考图片
    ↓
Sora-2 生成第二个视频片段 (使用上一帧作为参考)
    ↓
... (重复)
    ↓
合并所有片段 → 最终长视频
```

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/bu-bu-xxx/Video-chain.git
cd Video-chain
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的aihubmix API密钥：

```
AIHUBMIX_API_KEY=sk-your-api-key-here
```

## 使用方法

### 命令行模式 (CLI)

#### 基本用法

```bash
python cli.py --description "一只猫在花园里玩耍，追逐蝴蝶，然后在树下睡觉"
```

#### 带参考图片

```bash
python cli.py --description "机器人探索未来城市" --image robot.jpg
```

#### 自定义参数

```bash
python cli.py \
  --description "日出到日落的海滩景色" \
  --segments 5 \
  --size 1920x1080 \
  --duration 5 \
  --output my_videos
```

#### 命令行参数说明

- `--description, -d`: 视频需求描述（必需，中文）
- `--image, -i`: 参考图片路径（可选）
- `--segments, -s`: 视频片段数量（默认：3）
- `--size`: 视频尺寸，可选 `1280x720`, `720x1280`, `1920x1080`（默认：`1280x720`）
- `--duration`: 每个片段的持续时间（秒）（默认：4）
- `--output, -o`: 输出目录（默认：output）
- `--api-key`: API密钥（可选，也可通过环境变量设置）

### Web界面模式

#### 启动Web服务器

```bash
python app.py
```

#### 访问界面

打开浏览器，访问：

```
http://localhost:5000
```

#### Web界面功能

1. 输入视频描述
2. （可选）上传参考图片
3. 设置片段数量、时长、视频尺寸
4. 点击"生成视频"按钮
5. 等待生成完成（通常需要几分钟）
6. 在线预览或下载生成的视频

## API说明

### aihubmix API

本项目使用 [aihubmix](https://aihubmix.com) 提供的API服务：

- **Sora-2 / Sora-2-Pro**: 视频生成模型
- **Gemini-3-pro-preview**: 提示词生成模型

### 模型特点

#### Sora-2
- 支持文本到视频生成
- 支持图片参考输入
- 多种视频尺寸选择
- 2-10秒可调时长

#### Gemini-3-pro-preview
- 多模态理解（文本+图片）
- 中文优化
- 结构化输出支持

## 项目结构

```
Video-chain/
├── video_chain.py          # 核心工作流模块
├── cli.py                  # 命令行界面
├── app.py                  # Web应用
├── templates/
│   └── index.html          # Web界面模板
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
├── GOAL.md                # 开发目标文档
└── README.md              # 本文件
```

## 核心模块说明

### video_chain.py

包含 `VideoChainWorkflow` 类，提供以下主要方法：

- `generate_prompts()`: 使用Gemini生成视频片段提示词
- `generate_video_segment()`: 使用Sora-2生成单个视频片段
- `extract_last_frame()`: 从视频提取最后一帧
- `concatenate_videos()`: 合并所有视频片段
- `run_workflow()`: 运行完整工作流

## 开发环境

- Python 3.8+
- OpenCV (视频处理)
- MoviePy (视频合并)
- Flask (Web界面)
- OpenAI SDK (API调用)

## 测试

本项目包含完整的测试套件：

```bash
# 基本验证测试（无需依赖）
python test_basic_validation.py

# 单元测试（需要安装依赖）
pip install -r requirements.txt
python test_video_chain.py
```

详细测试文档请查看 [TESTING.md](TESTING.md)

## 注意事项

1. **API费用**: 使用aihubmix API会产生费用，请注意控制使用量
2. **生成时间**: 视频生成需要时间，建议从少量片段开始测试
3. **磁盘空间**: 确保有足够的磁盘空间存储生成的视频文件
4. **网络连接**: 需要稳定的网络连接访问API服务
5. **API密钥安全**: 不要将API密钥提交到公共仓库

## 安全性

本项目已实施以下安全措施：

- ✅ **防止路径遍历攻击**: 下载端点验证文件路径，防止访问未授权文件
- ✅ **XSS防护**: Web界面对用户输入和API响应进行适当转义
- ✅ **生产环境配置**: 默认禁用调试模式，通过环境变量控制
- ✅ **依赖版本锁定**: 使用具体版本范围防止意外的破坏性更新

**生产环境部署建议**:
1. 使用反向代理（如Nginx）而不是直接暴露Flask应用
2. 设置适当的访问控制和身份验证
3. 定期更新依赖包以修复安全漏洞
4. 使用HTTPS加密传输
5. 监控API使用情况防止滥用
6. 考虑使用 `host='127.0.0.1'` 仅允许本地访问，或配置防火墙规则

## 故障排查

### 问题：API密钥未设置

```
错误: API key is required
```

**解决方案**: 确保已创建 `.env` 文件并设置了 `AIHUBMIX_API_KEY`

### 问题：导入错误

```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**: 安装所需依赖

```bash
pip install -r requirements.txt
```

### 问题：视频生成失败

**解决方案**:
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看控制台输出的详细错误信息
4. 确认API配额是否充足

## 示例

### 示例1: 猫咪视频

```bash
python cli.py --description "一只橙色的小猫在客厅里玩耍，追逐毛线球，跳到沙发上，最后趴在窗台上看外面" --segments 4
```

### 示例2: 风景视频

```bash
python cli.py --description "清晨的山间，云雾缭绕，太阳慢慢升起，金色的阳光洒在山顶，鸟儿开始歌唱" --segments 5 --size 1920x1080
```

### 示例3: 科幻场景

```bash
python cli.py --description "未来城市，飞行汽车在空中穿梭，霓虹灯闪烁，机器人在街道上行走" --image cyberpunk.jpg --segments 3
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/bu-bu-xxx/Video-chain
- 问题反馈: https://github.com/bu-bu-xxx/Video-chain/issues

## 更新日志

### v1.0.0 (2025-12-07)

- ✨ 初始版本发布
- 🎬 实现基于Sora-2的视频片段生成
- 🤖 集成Gemini-3-pro-preview进行提示词生成
- 💻 提供CLI和Web两种使用方式
- 🔗 实现视频片段连贯性保证机制
- 🇨🇳 完整中文支持

---

**享受创作连贯视频的乐趣！** 🎉
