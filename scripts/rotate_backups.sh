#!/usr/bin/env bash
set -euo pipefail
ROOT="/mnt/c/Users/admin/Desktop/두리백업"
keep_core=14
keep_ext=8
keep_full=8

for L in CORE EXTENDED FULL; do
    mapfile -t files < <(find "$ROOT" -type f -name "${L}__*.tar.zst" | sort)
    count=${#files[@]}
    keep=$([[ "$L" == CORE ]] && echo $keep_core || ([[ "$L" == EXTENDED ]] && echo $keep_ext || echo $keep_full))
    
    if (( count > keep )); then
        del=$((count-keep))
        echo "[${L}] ${count}개 중 ${keep}개 유지, ${del}개 삭제"
        printf "%s\n" "${files[@]:0:$del}" | xargs -r rm -f
    else
        echo "[${L}] ${count}개 (${keep}개 이하, 삭제 없음)"
    fi
done

echo "[OK] 백업 회전 완료"
