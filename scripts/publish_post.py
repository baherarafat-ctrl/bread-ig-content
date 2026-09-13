#!/usr/bin/env python3
"""
Publish a rendered post PNG (already committed & pushed to this repo)
to Instagram via the Content Publishing API.

Reads credentials from environment variables:
  IG_USER_ID       - the bread.eg Instagram-scoped user id
  IG_ACCESS_TOKEN  - a valid Instagram User Access Token with
                     instagram_business_content_publish

Usage:
  python3 publish_post.py --image-url <raw.githubusercontent.com URL> --caption "..."
"""
import argparse
import os
import sys
import time
import urllib.parse
import urllib.request
import json

GRAPH = "https://graph.instagram.com/v19.0"


def call(url, data=None, method="POST"):
    if data:
        data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("ERROR:", body, file=sys.stderr)
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image-url", required=True)
    p.add_argument("--caption", required=True)
    args = p.parse_args()

    ig_user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]

    container = call(f"{GRAPH}/{ig_user_id}/media", {
        "image_url": args.image_url,
        "caption": args.caption,
        "access_token": token,
    })
    creation_id = container["id"]
    print("container created:", creation_id)

    # poll container status until FINISHED (usually instant for images)
    for _ in range(10):
        status = call(f"{GRAPH}/{creation_id}?fields=status_code&access_token={urllib.parse.quote(token)}", method="GET")
        if status.get("status_code") == "FINISHED":
            break
        time.sleep(2)

    result = call(f"{GRAPH}/{ig_user_id}/media_publish", {
        "creation_id": creation_id,
        "access_token": token,
    })
    print("published:", json.dumps(result))


if __name__ == "__main__":
    main()
