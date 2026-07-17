# AI 绘本配音工作区

本仓库保存儿童 AI 绘本的配音稿、生成脚本、角色音色配置和最终音频。项目面向 3–9 岁儿童，主要使用 Edge-TTS；点点使用已经激活的 MinMax 克隆音色。

## 固定角色音色

| 角色 | 服务 | 音色 |
| --- | --- | --- |
| 团团 | Edge-TTS | `zh-CN-YunxiaNeural` |
| 点点 | MinMax | `AIBook_diandian_edge_20260715174438` + 清脆嘹亮 V2 后期 |
| 旁白 | Edge-TTS | `zh-CN-XiaoxiaoNeural` + 磁性版参数 |

点点的最终参考试听为 `audio_output/cloned_samples/diandian_edge_cloned_bright_loud_v2.mp3`。旁白的最终参考试听为 `audio_output/narrator_candidates/narrator_magnetic_loud.mp3`。

## 在新电脑上恢复

1. 安装 Git、Python 3.11+ 和 FFmpeg，并确保 `python`、`git`、`ffmpeg`、`ffprobe` 在 PATH 中。
2. 克隆仓库：

   ```powershell
   git clone git@github.com:YangTrees/AIBook_Video_Audio.git
   cd AIBook_Video_Audio
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

3. 运行 `setup_minimax.ps1`，在本地输入 MinMax API Key。`.env` 已被 Git 忽略，禁止提交。
4. 在 Codex 中打开仓库。Codex 应先阅读 `AGENTS.md`，其中记录了音色和输出规则。

## 生成方式

- 纯 Edge 课程：运行对应的 `generate_lesson*_edge.py`。
- Edge + MinMax 混合课程：运行对应的 `generate_lesson*_mixed.py`。
- 配音稿保存在 `lesson*_voice_manifest.json`。
- 最终逐镜音频保存在 `audio_output/<lesson>/segments*`。
- 所有最终成品统一做响度标准化，目标约为 `-12 LUFS`，峰值不超过 `-0.5 dBTP`。

MinMax 克隆音色属于创建它的 MinMax 账号。新电脑必须使用同一账号的 API Key 才能继续调用现有 `voice_id`。如果更换账号，需要重新克隆音色并更新清单。

## 安全说明

- 永远不要提交 `.env`、API Key 或 GitHub Token。
- `audio_output/**/raw/` 和 `*_raw.mp3` 是可再生中间文件，不进入 Git。
- 已提交最终音频，换电脑后无需重新生成历史课程。
