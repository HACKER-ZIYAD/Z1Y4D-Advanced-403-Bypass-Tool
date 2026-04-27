#!/usr/bin/env python3
"""Verify the bypass tool works correctly"""
import subprocess
import sys

TEST_URLS = [
    "https://httpbin.org/status/403",
    "https://httpbin.org/status/401",
    "https://httpbin.org/get",
]

for url in TEST_URLS:
    print(f"\n{'='*60}\nTesting: {url}\n{'='*60}")
    subprocess.run([sys.executable, "bypass403.py", "-u", url, "-t", "10"])
