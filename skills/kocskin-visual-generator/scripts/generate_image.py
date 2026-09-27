#!/usr/bin/env python3
"""
KOCSKIN AI 素材生成器 — Cloudinary Image Generation API 呼叫腳本

用途：
  給定一段（或多段）視覺概念 prompt，呼叫 Cloudinary 的 Image Generation API
  （text_to_image 或 image_to_image）產出圖片，存到本機資料夾，並把每張圖
  對應的 prompt / model / seed 等資訊寫進同目錄的 manifest.json，方便追蹤
  「這張圖是怎麼生出來的」。

憑證處理原則（Welson 2026-08-25 決定）：
  - 不寫死在任何檔案裡。
  - 一律從環境變數 CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET / CLOUDINARY_CLOUD_NAME 讀取。
  - 每次執行前由 Claude 向 Welson 索取，用完即丟，不落地保存。

用法範例：
  export CLOUDINARY_API_KEY="..."
  export CLOUDINARY_API_SECRET="..."
  export CLOUDINARY_CLOUD_NAME="s55rhpbr"

  python3 generate_image.py \
      --prompt "A skincare serum bottle on marble counter, soft morning light, product photography" \
      --model-family nano-banana --model-tier premium \
      --aspect-ratio 4:3 --resolution 1K \
      --out ./output/concept_1.png

  # image_to_image（用商品實拍照當參考，只換場景，不竄改商品外觀）
  python3 generate_image.py \
      --prompt "Place the product from [1] on a marble kitchen counter, soft morning light" \
      --ref-url "https://res.cloudinary.com/.../product.jpg" \
      --out ./output/concept_2.png
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from base64 import b64encode


API_BASE = "https://api.cloudinary.com/v2"


def get_credentials():
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    missing = [
        name
        for name, val in [
            ("CLOUDINARY_API_KEY", api_key),
            ("CLOUDINARY_API_SECRET", api_secret),
            ("CLOUDINARY_CLOUD_NAME", cloud_name),
        ]
        if not val
    ]
    if missing:
        sys.exit(
            "缺少環境變數：" + ", ".join(missing) +
            "\n請先跟 Welson 索取本次測試用的 Cloudinary API Key / Secret / Cloud name，"
            "export 到環境變數後再執行本腳本。"
        )
    return api_key, api_secret, cloud_name


def build_auth_header(api_key, api_secret):
    token = b64encode(f"{api_key}:{api_secret}".encode()).decode()
    return f"Basic {token}"


def call_generate_api(endpoint, payload, api_key, api_secret, cloud_name):
    url = f"{API_BASE}/generate/{cloud_name}/{endpoint}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", build_auth_header(api_key, api_secret))
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"Cloudinary API 錯誤 (HTTP {e.code})：{err_body}")
    except urllib.error.URLError as e:
        sys.exit(f"連線失敗：{e}")


def download_asset(secure_url, out_path):
    with urllib.request.urlopen(secure_url, timeout=120) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)


def append_manifest(manifest_path, record):
    records = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []
    records.append(record)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(description="Cloudinary Image Generation API 呼叫工具")
    p.add_argument("--prompt", required=True, help="文字描述（1~4000字）")
    p.add_argument("--out", required=True, help="輸出圖片檔路徑，例如 ./output/concept_1.png")

    # model 選擇（擇一）
    p.add_argument("--model-id", help="直接指定模型 id，例如 nano-banana-2")
    p.add_argument("--model-family", help="模型家族，例如 nano-banana / flux / recraft / gpt-image / ideogram")
    p.add_argument("--model-tier", help="模型等級，例如 standard / premium（不填預設 standard）")

    # size（擇一）
    p.add_argument("--aspect-ratio", help="例如 4:3、1:1、9:16")
    p.add_argument("--resolution", choices=["0.5K", "1K", "2K"], default="1K")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)

    p.add_argument("--format", choices=["jpeg", "png", "webp"], default="png")
    p.add_argument("--seed", type=int)

    # image_to_image 用：參考圖（可重複給多個 --ref-url 或 --ref-asset-id，最多4張）
    p.add_argument("--ref-url", action="append", default=[], help="外部參考圖 HTTPS URL，可重複給")
    p.add_argument("--ref-asset-id", action="append", default=[], help="Cloudinary 已存在的 managed asset id，可重複給")

    p.add_argument("--manifest", default=None, help="manifest.json 路徑，預設與 --out 同資料夾")

    args = p.parse_args()

    api_key, api_secret, cloud_name = get_credentials()

    payload = {"prompt": args.prompt, "format": args.format}

    if args.model_id:
        payload["model"] = {"id": args.model_id}
    elif args.model_family:
        model = {"family": args.model_family}
        if args.model_tier:
            model["tier"] = args.model_tier
        payload["model"] = model

    if args.width and args.height:
        payload["image_size"] = {"width": args.width, "height": args.height}
    elif args.aspect_ratio:
        payload["image_size"] = {"aspect_ratio": args.aspect_ratio, "resolution": args.resolution}

    if args.seed is not None:
        payload["seed"] = args.seed

    reference_images = []
    for url in args.ref_url:
        reference_images.append({"source_type": "url", "url": url})
    for asset_id in args.ref_asset_id:
        reference_images.append({"source_type": "managed_asset", "asset_id": asset_id})

    if reference_images:
        payload["reference_images"] = reference_images
        endpoint = "image_to_image"
    else:
        endpoint = "text_to_image"

    print(f"呼叫 {endpoint} ... prompt: {args.prompt[:60]}{'...' if len(args.prompt) > 60 else ''}")
    result = call_generate_api(endpoint, payload, api_key, api_secret, cloud_name)

    assets = result.get("data", {}).get("assets", [])
    if not assets:
        sys.exit(f"回應中沒有 assets，完整回應：{json.dumps(result, ensure_ascii=False)}")

    asset = assets[0]
    secure_url = asset.get("storage", {}).get("secure_url")
    if not secure_url:
        sys.exit(f"回應沒有 secure_url，可能是 managed_asset 型態，完整回應：{json.dumps(result, ensure_ascii=False)}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    download_asset(secure_url, args.out)
    print(f"已存檔：{args.out}")

    quota = result.get("limits", {}).get("addons_quota", [])
    if quota:
        q = quota[0]
        print(f"額度：本次用了 {q.get('used_by_request')}，剩餘 {q.get('remaining')} / {q.get('limit')}")

    manifest_path = args.manifest or os.path.join(
        os.path.dirname(os.path.abspath(args.out)) or ".", "manifest.json"
    )
    append_manifest(
        manifest_path,
        {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "out_file": args.out,
            "endpoint": endpoint,
            "prompt": args.prompt,
            "payload": payload,
            "model_used": asset.get("model"),
            "seed_used": asset.get("seed"),
            "width": asset.get("width"),
            "height": asset.get("height"),
            "request_id": result.get("request_id"),
        },
    )
    print(f"已記錄到 manifest：{manifest_path}")


if __name__ == "__main__":
    main()
