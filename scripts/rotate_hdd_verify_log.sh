#!/usr/bin/env bash
f="var/logs/hdd_verify.log"
[ -f "$f" ] && [ $(stat -c%s "$f") -gt 5242880 ] && mv "$f" "${f}.$(date +%Y%m%d_%H%M%S)"
