# minimax-h3-video for OpenClaw

Minimal OpenClaw Skill for MiniMax H3 video generation.

## What it does

Chat / slash-command intent → OpenClaw rewrites a professional prompt → MiniMax H3 → waits for completion → returns `video_url`.

It supports:
- Text-to-video
- First-frame image-to-video using a public image URL
- 768P / 2K
- 4–15 seconds
- 16:9 / 9:16 / 1:1 and other H3 ratios

## Install

Copy this whole folder to:

`~/.openclaw/workspace/skills/minimax-h3-video`

or install the local folder with a recent OpenClaw build:

`openclaw skills install ./minimax-h3-video --as minimax-h3-video`

Then configure the Skill's `MINIMAX_API_KEY` in OpenClaw. The `SKILL.md` declares `MINIMAX_API_KEY` as its primary environment variable.

For China API, the script defaults to:

`https://api.minimaxi.com`

For Global API, set:

`MINIMAX_API_BASE=https://api.minimax.io`

Start a new OpenClaw session after installing if the Skill does not appear immediately.

## Quick terminal smoke test

With `MINIMAX_API_KEY` available to the process:

```bash
python3 scripts/h3_video.py \
  --prompt "A silver electric car drives through a futuristic city at night, cinematic automotive commercial, smooth tracking shot" \
  --duration 5 \
  --resolution 768P \
  --ratio 16:9
```

Success output contains:

```json
{"ok": true, "task_id": "...", "video_url": "https://...mp4"}
```

## Channel demo prompts

### Text-to-video

> 用 MiniMax H3 生成一个 5 秒新能源汽车广告。夜晚未来城市，一辆银色新能源汽车驶过雨后街道，低机位跟拍，霓虹倒影，高端电影级汽车广告。16:9，768P。直接生成，完成后把视频链接给我。

### Product-image animation

> 把我提供的产品图做成 5 秒高级广告镜头。保持产品主体、外形和品牌特征不变，让灯光从左向右扫过，镜头缓慢推进并轻微环绕。用 MiniMax H3，16:9，768P，完成后把视频链接给我。

Note: for this minimal Skill, image-to-video expects the image to be available at a public HTTPS URL.
