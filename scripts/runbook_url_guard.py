#!/usr/bin/env python3
import glob
import re
import sys
import urllib.parse

RUNBOOK_URL_RE = re.compile(r'^\s*runbook_url:\s*["\']?([^"\']+)["\']?')
HTTPS_RE = re.compile(r"^https://")


def check_file(path):
    issues = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            match = RUNBOOK_URL_RE.search(line)
            if match:
                url = match.group(1)
                if not HTTPS_RE.match(url):
                    issues.append(f"{path}:{line_num}: non-HTTPS URL: {url}")
                try:
                    parsed = urllib.parse.urlparse(url)
                    if not parsed.netloc:
                        issues.append(f"{path}:{line_num}: invalid URL format: {url}")
                except Exception as e:
                    issues.append(f"{path}:{line_num}: URL parse error: {url} ({e})")
    return issues


def main():
    issues = []
    for path in glob.glob("prometheus/rules/**/*.y*ml", recursive=True):
        issues += check_file(path)
    if issues:
        for issue in issues:
            print(issue)
        sys.exit(1)


if __name__ == "__main__":
    main()
