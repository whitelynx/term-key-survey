#!/bin/bash

TKS=$(dirname "$(readlink -f "$0")")/term-key-survey.py
XEPHYR=$(which Xephyr)

width=1280
height=800

function run() {
	termname="$(basename "$1")"
	startx "$@" "$TKS" "$termname" -- "$XEPHYR" -screen ${width}x${height} -title "$termname" :1
}

run "$(which urxvt)" -g 100x40 -bg blue4 -fg White -e
run "$(which st)" -g 100x40 -e
run "$(which rxvt)" -g 100x40 -bg blue4 -fg White -e
run "$(which xterm)" -g 100x40 -bg blue4 -fg White -e
run "$(which Eterm)" -g 100x40 -b blue4 -f White -e
run "$(which lxterminal)" --geometry=100x40 -e
run "$(which konsole)" -e
run "$(which alacritty)" --dimensions 100 40 -e
run "$(which pterm)" -geometry 100x40 -bg blue4 -fg White -e
run "$(which kitty)" -c /usr/lib/kitty/kitty/kitty.conf -o initial_window_width=$width -o initial_window_height=$height
