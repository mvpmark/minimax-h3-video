#!/usr/bin/env python3
"""Minimal MiniMax H3 video generator for OpenClaw skills.

Uses only Python standard library.
Create: POST /v2/video_generation
Query:  GET  /v2/query/video_generation/{task_id}
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def _request_json(method, url, api_key, payload=None, timeout=60):
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body[:1200]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e


def _extract_status(obj):
    task = obj.get("task") if isinstance(obj, dict) else None
    if isinstance(task, dict):
        status = task.get("status") or task.get("state")
        if status:
            return str(status)
    if isinstance(obj, dict):
        status = obj.get("status") or obj.get("state")
        if status:
            return str(status)
    return "Unknown"


def _extract_video_url(obj):
    if not isinstance(obj, dict):
        return None

    # Official H3 examples: task.content.url
    task = obj.get("task")
    if isinstance(task, dict):
        content = task.get("content")
        if isinstance(content, dict) and content.get("url"):
            return content["url"]
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("url"):
                    return item["url"]
        for key in ("video_url", "url"):
            if task.get(key):
                return task[key]

    # Compatibility with alternate response layouts.
    for key in ("video_url", "url"):
        if obj.get(key):
            return obj[key]

    data = obj.get("data")
    if isinstance(data, dict):
        for key in ("video_url", "url"):
            if data.get(key):
                return data[key]

    return None


def _extract_failure(obj):
    if not isinstance(obj, dict):
        return "Unknown failure"
    task = obj.get("task")
    candidates = []
    if isinstance(task, dict):
        candidates += [task.get("error"), task.get("message"), task.get("fail_reason")]
    candidates += [obj.get("error"), obj.get("message"), obj.get("status_msg")]
    for value in candidates:
        if value:
            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False)
            return str(value)
    return json.dumps(obj, ensure_ascii=False)[:1500]


def main():
    parser = argparse.ArgumentParser(description="Generate a MiniMax H3 video and return its URL")
    parser.add_argument("--prompt", required=True, help="Video prompt")
    parser.add_argument("--image-url", help="Optional public image URL used as the first frame")
    parser.add_argument("--duration", type=int, default=5, help="Duration in seconds; default 5")
    parser.add_argument("--resolution", default="768P", choices=["768P", "2K"], help="Default 768P")
    parser.add_argument(
        "--ratio",
        default="16:9",
        choices=["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
        help="Aspect ratio; default 16:9",
    )
    parser.add_argument("--poll-interval", type=int, default=8, help="Polling interval seconds")
    parser.add_argument("--timeout", type=int, default=900, help="Maximum wait seconds")
    args = parser.parse_args()

    if not (4 <= args.duration <= 15):
        parser.error("--duration must be between 4 and 15 seconds for MiniMax H3")

    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "error": "MINIMAX_API_KEY is not configured"}, ensure_ascii=False))
        return 2

    api_base = os.environ.get("MINIMAX_API_BASE", "https://api.minimaxi.com").rstrip("/")

    content = [{"type": "text", "text": args.prompt}]
    if args.image_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": args.image_url},
            "role": "first_frame",
        })

    payload = {
        "model": "MiniMax-H3",
        "content": content,
        "resolution": args.resolution,
        "duration": args.duration,
        "ratio": args.ratio,
    }

    try:
        create = _request_json("POST", f"{api_base}/v2/video_generation", api_key, payload=payload)
        task_id = create.get("task_id") if isinstance(create, dict) else None
        if not task_id:
            raise RuntimeError(f"No task_id returned: {json.dumps(create, ensure_ascii=False)[:1500]}")

        deadline = time.time() + args.timeout
        last_status = None

        while time.time() < deadline:
            result = _request_json(
                "GET",
                f"{api_base}/v2/query/video_generation/{urllib.parse.quote(str(task_id), safe='')}",
                api_key,
            )
            status = _extract_status(result)
            norm = status.strip().lower()

            if norm in {"success", "succeeded", "completed", "complete", "done"}:
                url = _extract_video_url(result)
                if not url:
                    raise RuntimeError(
                        "Task succeeded but no video URL was found in response: "
                        + json.dumps(result, ensure_ascii=False)[:1500]
                    )
                print(json.dumps({
                    "ok": True,
                    "task_id": str(task_id),
                    "status": status,
                    "video_url": url,
                    "model": "MiniMax-H3",
                    "resolution": args.resolution,
                    "duration": args.duration,
                    "ratio": args.ratio,
                }, ensure_ascii=False))
                return 0

            if norm in {"failed", "failure", "error", "cancelled", "canceled"}:
                raise RuntimeError(f"Generation failed ({status}): {_extract_failure(result)}")

            if status != last_status:
                print(json.dumps({"ok": True, "task_id": str(task_id), "status": status}, ensure_ascii=False), file=sys.stderr)
                last_status = status

            time.sleep(max(2, args.poll_interval))

        raise RuntimeError(f"Timed out after {args.timeout}s waiting for task {task_id}")

    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
