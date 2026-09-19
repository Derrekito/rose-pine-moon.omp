#!/usr/bin/env python3
"""Generate the three Rosé Pine variants from one shared layout.

The variants differ only in their base palette, so the layout lives here once.
Run from anywhere:  tools/build.py          (writes *.omp.json, CRLF like upstream)
                    tools/build.py --check  (exit 1 if the files are out of date)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json"

VARIANTS = {
    "rose-pine.omp.json": {
        "base": "#191724", "surface": "#1f1d2e", "overlay": "#26233a",
        "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
        "love": "#eb6f92", "gold": "#f6c177", "rose": "#ebbcba",
        "pine": "#31748f", "foam": "#9ccfd8", "iris": "#c4a7e7",
        "highlight-low": "#21202e", "highlight-med": "#403d52", "highlight-high": "#524f67",
    },
    "moon.omp.json": {
        "base": "#232136", "surface": "#2a273f", "overlay": "#393552",
        "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
        "love": "#eb6f92", "gold": "#f6c177", "rose": "#ea9a97",
        "pine": "#3e8fb0", "foam": "#9ccfd8", "iris": "#c4a7e7",
        "highlight-low": "#2a283e", "highlight-med": "#44415a", "highlight-high": "#56526e",
    },
    "dawn.omp.json": {
        "base": "#faf4ed", "surface": "#fffaf3", "overlay": "#f2e9e1",
        "muted": "#9893a5", "subtle": "#797593", "text": "#575279",
        "love": "#b4637a", "gold": "#ea9d34", "rose": "#d7827e",
        "pine": "#286983", "foam": "#56949f", "iris": "#907aa9",
        "highlight-low": "#f4ede8", "highlight-med": "#dfdad9", "highlight-high": "#cecacd",
    },
}

# Semantic aliases: restyle the theme by repointing these, not by editing segments.
ALIASES = {
    "true": "p:pine", "false": "p:love", "time": "p:muted",

    # Fills are Rosé Pine's own layered neutrals, one tone per chip (the path is
    # the darker of the two main chips, git the lighter). Colour lives in the TEXT,
    # which is how Rosé Pine itself uses its accents; love, gold and rose are
    # never used as a fill.
    "step-0": "p:surface",                      # moon phase, and the root '#': a shade darker than the path
    "step-1": "p:highlight-high",               # user@host over SSH
    "step-2": "p:overlay",                      # path
    "step-3": "p:highlight-med",                # git
    "step-4": "p:surface",                      # docker context, Python venv

    "moon": "p:iris",                           # moon-phase glyph (Moon variant)
    "root": "p:love",                           # the '#' shown in a root shell
    "lock": "p:gold",                           # padlock in a directory you cannot write to
    "battery": "p:gold",                        # low-battery warning
    "session-fg": "p:text",
    "path-fg": "p:foam",
    "git-clean": "p:subtle",                    # nothing to commit: branch recedes
    "git": "p:iris",                            # uncommitted changes: branch lights up
    "git-alert": "p:love",                      # conflicts / unfinished merge, rebase...
    "docker": "p:foam",
    "venv": "p:pine",                           # active Python virtualenv name
}

# Per-variant tweaks on top of the shared layout.
ARROW = "\ue0b0"


def filled(kind, fg, bg, template, **extra):
    # leading_powerline_symbol is only drawn when the chip is the first filled
    # one on the line; a half block gives it a flat edge instead of a notch.
    return {"type": kind, "style": "powerline", "powerline_symbol": ARROW,
            "leading_powerline_symbol": "\u2590",
            "foreground": fg, "background": bg, "template": template, **extra}


# The 28 Nerd Font moon glyphs run new -> full -> new from U+E38D. The phase is
# worked out in the template: seconds since a known new moon (2000-01-06 18:14
# UTC), modulo the synodic month, scaled to 0..27.
MOON_PHASE = ("{{ $i := mod (div (mul (mod (sub now.Unix 947182440) 2551443) 28) 2551443) 28 }}"
              # no leading space: the flat-edge half block already pads the left side
              "{{ printf \"%c\" (add 58253 $i) }} ")

# Per-variant extras on top of the shared layout: segments put at the very front.
OVERRIDES = {
    "moon.omp.json": {"lead": [
        filled("text", "p:moon", "p:step-0", MOON_PHASE)]},
}


LEFT = [
    # What leads the line means something, on a chip a shade darker than the path:
    # (Moon only) tonight's moon phase, see OVERRIDES; and a '#' when root.
    filled("root", "p:root", "p:step-0", "# "),
    filled("session", "p:session-fg", "p:step-1",
           "{{ if .SSHSession }} \ueb39 {{ .UserName }}@{{ .HostName }} {{ end }}"),
    filled("path", "p:path-fg", "p:step-2",
           " {{ if not .Writable }}<p:lock>\uf023</> {{ end }}{{ .Path }} ",
           options={"home_icon": "~", "folder_icon": "\u2026",
                       "style": "agnoster_short", "max_depth": 3}),
    # Deliberately sparse: icon + branch name. No counts, ahead/behind or stash.
    # Two things do get through, both as text colour: subtle = clean, iris =
    # uncommitted changes; and an alert state in love, because it blocks work until it
    # is dealt with: merge conflicts, or a merge/rebase/cherry-pick/revert that
    # is still in progress (.HEAD already spells those out, with their own icon).
    filled("git", "p:git-clean", "p:step-3",
           " {{ .HEAD }}"
           # a conflicted file is counted on both sides, so take the larger, not the sum
           "{{ $c := .Working.Unmerged }}{{ if gt .Staging.Unmerged $c }}{{ $c = .Staging.Unmerged }}{{ end }}"
           "{{ if gt $c 0 }} \uf071 {{ $c }}{{ end }} ",
           foreground_templates=[
               "{{ if or (gt .Working.Unmerged 0) (gt .Staging.Unmerged 0) .Rebase .Merge .CherryPick .Revert }}p:git-alert{{ end }}",
               "{{ if or (.Working.Changed) (.Staging.Changed) }}p:git{{ end }}"],
           options={
               "branch_icon": "\ue725 ", "branch_gone_icon": "", "cherry_pick_icon": "\ue29b ",
               "commit_icon": "\uf417 ", "fetch_status": True,
               "fetch_stash_count": False, "fetch_upstream_icon": False,
               "merge_icon": "\ue727 ", "no_commits_icon": "\uf0c3 ",
               "rebase_icon": "\ue728 ", "revert_icon": "\uf0e2 ", "tag_icon": "\uf412 "}),
    filled("docker", "p:docker", "p:step-4", " \uf308 {{ .Context }} "),
    # No language-version segments: the version is rarely what you need at the
    # prompt. The one exception worth a chip is *which* Python venv is active.
    filled("python", "p:venv", "p:step-4", "{{ if .Venv }} \ue73c {{ .Venv }} {{ end }}",
           options={"display_mode": "environment", "fetch_version": False,
                       "fetch_virtual_env": True, "display_default": False,
                       "home_enabled": True}),
]

RIGHT = [
    {"type": "battery", "style": "plain", "foreground": "p:battery",
     "template": "{{ if and (eq .State.String \"Discharging\") (le .Percentage 25) }}"
                 "\U000f0083 {{ .Percentage }}% {{ end }}"},
    {"type": "status", "style": "plain", "foreground": "p:false",
     "template": "\uf00d {{ .Code }} "},
    {"type": "executiontime", "style": "plain", "foreground": "p:true",
     "foreground_templates": ["{{ if .Code }}p:false{{ end }}"],
     "template": "\U000f051f {{ .FormattedMs }} ",
     "options": {"threshold": 500, "style": "austin"}},
]

PROMPT = [
    {"type": "status", "style": "plain", "foreground": "p:true",
     "foreground_templates": ["{{ if gt .Code 0 }}p:false{{ end }}"],
     "template": "\u276f ", "options": {"always_enabled": True}},
]


def config(name, palette):
    over = OVERRIDES.get(name, {})
    left = over.get("lead", []) + LEFT
    return {
        "$schema": SCHEMA,
        "version": 2,
        "final_space": False,
        "console_title_template": "{{ .Shell }} in {{ .Folder }}",
        "palette": {**palette, **ALIASES, **over.get("aliases", {})},
        "transient_prompt": {
            "foreground": "p:time",
            "template": "{{ now | date \"15:04:05\" }} {{ if gt .Code 0 }}"
                        "<p:false>\u276f</>{{ else }}<p:true>\u276f</>{{ end }} ",
        },
        "secondary_prompt": {"foreground": "p:time", "template": "\u276f\u276f "},
        "blocks": [
            {"type": "prompt", "alignment": "left", "newline": True, "segments": left},
            {"type": "prompt", "alignment": "right", "segments": RIGHT},
            {"type": "prompt", "alignment": "left", "newline": True, "segments": PROMPT},
        ],
    }


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for name, palette in VARIANTS.items():
        text = json.dumps(config(name, palette), indent=4, ensure_ascii=True) + "\n"
        data = text.replace("\n", "\r\n").encode("ascii")
        path = ROOT / name
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(name)
        else:
            path.write_bytes(data)
            print("wrote", name)
    if stale:
        sys.exit("out of date, run tools/build.py: " + ", ".join(stale))


if __name__ == "__main__":
    main()
