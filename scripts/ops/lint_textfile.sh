#!/usr/bin/env bash
# Textfile Prometheus format linter
# Observability Contract v1: pre-commit/CI validation

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
LINT_ERR_LOG="${LINT_ERR_LOG:-.reports/synth/lint_err.log}"

mkdir -p "$(dirname "$LINT_ERR_LOG")"

lint_file() {
    local f="$1"
    local errors=0
    
    # 1. UTF-8 validation (no BOM, valid encoding)
    if ! iconv -f utf-8 -t utf-8 "$f" -o /dev/null 2>/dev/null; then
        echo "[ERROR] UTF8_FAIL: $f" >> "$LINT_ERR_LOG"
        echo "UTF8_FAIL: $f" >&2
        errors=$((errors + 1))
    fi
    
    # 2. No commas in metric values (but allow commas in labels)
    # Check if comma appears outside of label braces {}
    if awk '
        {
            # Skip comments
            if (/^[[:space:]]*#/) next
            # Extract value part (after last space)
            match($0, /[[:space:]]+([0-9.eE+-]+)$/, arr)
            if (arr[1] == "") next
            # Check if comma appears in value part
            if (arr[1] ~ /,/) {
                print "COMMA_IN_VALUE"
                exit 1
            }
        }
    ' "$f" 2>/dev/null | grep -q "COMMA_IN_VALUE"; then
        echo "[ERROR] COMMA_FAIL: $f" >> "$LINT_ERR_LOG"
        echo "COMMA_FAIL: $f (comma found in metric value)" >&2
        errors=$((errors + 1))
    fi
    
    # 3. No CRLF (Windows line endings)
    if grep -q $'\r' "$f" 2>/dev/null; then
        echo "[ERROR] CRLF_FAIL: $f" >> "$LINT_ERR_LOG"
        echo "CRLF_FAIL: $f (CRLF found)" >&2
        errors=$((errors + 1))
    fi
    
    # 4. Format validation: lines are either comments (#) or metric lines (name{labels} value)
    while IFS= read -r line; do
        # Skip empty lines
        [ -z "$line" ] && continue
        
        # Skip comments
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Check for invalid characters (Inf/NaN)
        if [[ "$line" =~ (Inf|NaN|inf|nan) ]]; then
            echo "[ERROR] INFNAN_FAIL: $f (line: $line)" >> "$LINT_ERR_LOG"
            echo "INFNAN_FAIL: $f (Inf/NaN found)" >&2
            errors=$((errors + 1))
            continue
        fi
        
        # Basic format: should have at least 2 fields (name{labels} value) or be a comment
        if ! [[ "$line" =~ ^[^[:space:]]+[[:space:]]+[0-9.eE+-]+$ ]] && \
           ! [[ "$line" =~ ^[^[:space:]]+\{.*\}[[:space:]]+[0-9.eE+-]+$ ]]; then
            echo "[ERROR] FORMAT_FAIL: $f (line: $line)" >> "$LINT_ERR_LOG"
            echo "FORMAT_FAIL: $f (invalid format)" >&2
            errors=$((errors + 1))
        fi
    done < "$f"
    
    return $errors
}

main() {
    local failed=0
    
    # Find all .prom files
    while IFS= read -r -d '' f; do
        if ! lint_file "$f"; then
            failed=$((failed + 1))
        fi
    done < <(find "$TEXTFILE_DIR" -name "*.prom" -type f -print0 2>/dev/null || true)
    
    if [ $failed -gt 0 ]; then
        echo "[ERROR] Lint failed: $failed file(s) with errors" >&2
        exit 1
    else
        echo "[OK] All textfile metrics passed linting"
        exit 0
    fi
}

main "$@"

