notify() {
  local msg="$1"
  if [[ -n "${NTFY_URL:-}" ]]; then
    curl -fsS -H "Title: DuRi Backup" -d "$msg" "$NTFY_URL" >/dev/null 2>&1 || true
  elif [[ -n "${NTFY_TOPIC:-}" ]]; then
    curl -fsS -H "Title: DuRi Backup" -d "$msg" "https://ntfy.sh/$NTFY_TOPIC" >/dev/null 2>&1 || true
  fi
}
with_trap() {
  local task="$1"
  trap 'rc=$?; [[ $rc -ne 0 ]] && notify "❌ '"$task"' failed (rc=$rc)"; rm -f "$LOCK" "${ARCHIVE}.partial" 2>/dev/null; exit $rc' INT TERM ERR
  trap 'rm -f "$LOCK" "${ARCHIVE}.partial" 2>/dev/null; notify "✅ '"$task"' ok"' EXIT
}
