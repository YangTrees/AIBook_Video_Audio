# Codex 工作说明

## 项目目标

为 3–9 岁儿童绘本提取分镜台词并生成逐镜配音。处理新课程时，先读取上下集脚本，排除画面、动作和关键帧说明，再建立 `lessonNN_voice_manifest.json`。

## 固定音色（除非用户明确修改）

- 团团：Edge-TTS `zh-CN-YunxiaNeural`。
- 点点：MinMax 克隆音色 `AIBook_diandian_edge_20260715174438`，默认 `speed=0.98`、`vol=1.0`、`pitch=1`、`emotion=happy`。
- 旁白：Edge-TTS `zh-CN-XiaoxiaoNeural`。

点点最终选定的是普通嘹亮版，不要使用 `diandian_crisp_*` 或 `diandian_crisp_de_nasal_*` 实验版本。

## 音频规则

- 标准普通话，保留原稿内容，不擅自删词。
- 每个说话人单独输出文件，命名为 `upper_01_narrator.mp3` 等可排序格式。
- 最终音频使用 FFmpeg `loudnorm=I=-12:TP=-0.5:LRA=5`，48 kHz、192 kbps MP3。
- 输出逐镜文件，并生成上下集按台词顺序拼接的完整试听。
- 完成后用 `ffprobe` 检查格式与时长，并报告超过镜头时间的段落。

## 密钥与可移植性

- 从项目根目录 `.env` 读取 MinMax 配置；不得显示、提交或硬编码 API Key。
- 新环境缺少 `.env` 时，引导用户复制 `.env.example` 并运行 `setup_minimax.ps1`。
- 所有新增脚本使用项目相对路径，禁止写入本机绝对路径。

