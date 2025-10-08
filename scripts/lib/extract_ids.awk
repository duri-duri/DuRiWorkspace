# locale-safe schema extractor with built-in dedupe + optional MAXN cap
BEGIN {
  RE  = "([a-z][a-z0-9_-]*([.][a-z0-9_-]+)+[.]v[0-9]+([.][0-9]+)?)"
  max = (MAXN + 0)  # -v MAXN=3 형식으로 주면 상한 적용, 미지정이면 0(무제한)
}
{
  l = $0; gsub(/^[ \t]+|[ \t]+$/, "", l)
  id = ""
  if (match(l, /"id"[[:space:]]*:[[:space:]]*"([^"]+)"/, m) && m[1] ~ RE) id = m[1]
  else if (match(l, RE, m)) id = m[1]
  if (id != "" && !seen[id]++) {
    print id
    if (max > 0) { c++; if (c >= max) exit }
  }
}
