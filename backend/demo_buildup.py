#!/usr/bin/env python3
"""Apply all demo stages via the API (no screenshots).

  python demo_buildup.py --api http://127.0.0.1:8000
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

from sample_data import DEMO_STAGES


def post(api: str, path: str):
    req = urllib.request.Request(
        f"{api.rstrip('/')}{path}",
        method="POST",
        data=b"",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--api", default="http://127.0.0.1:8000")
    args = p.parse_args()
    for stage in DEMO_STAGES:
        info = post(args.api, f"/demo/stages/{stage['id']}")
        print(f"{info['id']}: {info['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
