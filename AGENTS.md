# Codex 工作说明

## 项目目标

为 3–9 岁儿童绘本提取分镜台词并生成逐镜配音。处理新课程时，先读取上下集脚本，排除画面、动作和关键帧说明，再建立 `lessonNN_voice_manifest.json`。

## 固定音色（除非用户明确修改）

- 团团：Edge-TTS `zh-CN-YunxiaNeural`。
- 点点：MinMax 克隆音色 `AIBook_diandian_edge_20260715174438`，默认 `speed=0.98`、`vol=1.0`、`pitch=1`、`emotion=happy`；后期使用清脆嘹亮 V2 参数。
- 旁白：Edge-TTS `zh-CN-XiaoxiaoNeural`，使用磁性版参数：`rate=-3%`、`pitch=-8Hz`、`volume=+5%`。

点点最终选定的是 `diandian_edge_cloned_bright_loud_v2.mp3` 对应的清脆嘹亮 V2 后期，不要使用早期的 `diandian_crisp_*` 或 `diandian_crisp_de_nasal_*` 实验版本。旁白以 `audio_output/narrator_candidates/narrator_magnetic_loud.mp3` 为参考。

## 音频规则

- 标准普通话，保留原稿内容，不擅自删词。
- 每个说话人单独输出文件，命名为 `upper_01_narrator.mp3` 等可排序格式。
- 团团使用 FFmpeg `loudnorm=I=-12:TP=-0.5:LRA=5`。
- 点点后期：`highpass=f=100`，380 Hz -2.5 dB，950 Hz -1.5 dB，2.9 kHz +2.8 dB，5.2 kHz +2 dB，轻度压缩，最终 `-11 LUFS`、`-0.5 dBTP`。
- 旁白后期：`highpass=f=70`，180 Hz +1.8 dB，420 Hz +1.2 dB，900 Hz -0.8 dB，2.8 kHz +1.2 dB，轻度压缩，最终 `-11.5 LUFS`、`-0.5 dBTP`。
- 最终统一输出 48 kHz、192 kbps MP3。
- 输出逐镜文件，并生成上下集按台词顺序拼接的完整试听。
- 完成后用 `ffprobe` 检查格式与时长，并报告超过镜头时间的段落。

## 密钥与可移植性

- 从项目根目录 `.env` 读取 MinMax 配置；不得显示、提交或硬编码 API Key。
- 新环境缺少 `.env` 时，引导用户复制 `.env.example` 并运行 `setup_minimax.ps1`。
- 所有新增脚本使用项目相对路径，禁止写入本机绝对路径。
