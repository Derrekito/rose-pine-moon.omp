#!/usr/bin/env bash
# Regenerate assets/*.png from the current themes, rendered against a throwaway
# demo repo so the gallery always shows the same representative state.
# Needs: oh-my-posh, git, rsvg-convert.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
demo="$tmp/rose-pine.omp"; mkdir -p "$demo"; cd "$demo"

git init -q -b main .
git -c user.name=demo -c user.email=demo@example.com commit -q --allow-empty -m init
printf 'print("hi")\n' > main.py; echo a > a.txt; echo b > b.txt
git add -A; git -c user.name=demo -c user.email=demo@example.com commit -q -m files
echo change >> a.txt; echo change >> b.txt; echo staged > c.txt; git add c.txt

render() { # <variant> <base colour>
  env -u POSH_SESSION_ID -u POSH_CONFIG -u POSH_SHELL -u POSH_SHELL_VERSION \
      HOME="$tmp" VIRTUAL_ENV="$tmp/.venv" \
    oh-my-posh config export image --config "$root/$1.omp.json" \
      --output "$tmp/$1.svg" --terminal-width 72 --background-color "$2" >/dev/null
  rsvg-convert -w 1280 "$tmp/$1.svg" -o "$root/assets/$1.png"
  echo "assets/$1.png"
}
render rose-pine '#191724'
render moon      '#232136'
render dawn      '#faf4ed'
