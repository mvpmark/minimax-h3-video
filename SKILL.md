---
name: minimax-h3-video
description: Generate commercial short video clips with MiniMax H3 from a text brief or a first-frame image. Use when the user asks to create, generate, animate, or turn a product image into a short video with MiniMax H3.
user-invocable: true
metadata: { "openclaw": { "emoji": "🎬", "requires": { "bins": ["python3"], "env": ["MINIMAX_API_KEY"] }, "primaryEnv": "MINIMAX_API_KEY" } }
---

# MiniMax H3 Video

Use this skill when the user wants MiniMax H3 to generate a short video.

## Default demo behavior

For fast, reliable customer demos, default to:
- model: `MiniMax-H3`
- resolution: `768P`
- duration: `5` seconds
- ratio: `16:9`
- China API base: `https://api.minimaxi.com`

If the user explicitly requests another supported duration, resolution, or ratio, pass it through.

## Workflow

1. Understand the user's business brief.
2. Rewrite it into a compact professional video-generation prompt. Preserve brand/product facts and do not invent factual claims.
3. If the user supplied a publicly reachable image URL and wants image-to-video, pass it as `--image-url`.
4. Run the helper script with the `exec` tool on the host:

```bash
python3 "{baseDir}/scripts/h3_video.py" \
  --prompt "<professional prompt>" \
  --duration 5 \
  --resolution 768P \
  --ratio 16:9
```

For first-frame image-to-video:

```bash
python3 "{baseDir}/scripts/h3_video.py" \
  --prompt "<professional prompt describing motion/camera/lighting>" \
  --image-url "https://public.example.com/product.jpg" \
  --duration 5 \
  --resolution 768P \
  --ratio 16:9
```

5. The script waits for the asynchronous MiniMax task to finish.
6. On success it prints a JSON object containing `video_url`.
7. Return the video URL to the user clearly. Do not expose the API key.

## Prompt guidelines

Prefer concrete cinematic instructions:
- subject and environment
- action/motion
- camera movement
- lighting
- visual style
- continuity constraints

For product-image animation, explicitly say to preserve the product's identity, shape, logo, and core visual features unless the user asks otherwise.

## Failure handling

If the script returns an error:
- report the short error message;
- do not print or reveal `MINIMAX_API_KEY`;
- if the service says the task failed, suggest retrying once with 5 seconds + 768P + 16:9 and a simpler prompt.

## Examples users can say

- “用 H3 做一个 5 秒新能源汽车广告，16:9。”
- “把这张产品图做成 5 秒高级广告镜头。”
- “用 MiniMax H3 生成视频，完成后把链接给我。”
