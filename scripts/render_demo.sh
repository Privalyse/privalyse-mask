#!/bin/bash
# Script to record and render the demo GIF using asciinema and agg

# 1. Record
# asciinema rec -c "python examples/demo_recording.py" assets/demo.cast

# 2. Render with agg (asciinema gif generator)
# Ensure you have a Nerd Font installed and configured!
# We use "JetBrainsMono Nerd Font" as an example.
# Download agg: https://github.com/asciinema/agg

echo "Generating GIF..."
# Using Noto Color Emoji for better emoji support and standard monospace font
agg --font-family "DejaVu Sans Mono, Noto Color Emoji" --font-size 20 --theme "dracula" --speed 1.5 public/demo.cast public/privalyse-mask-demo.gif

echo "Done! Check public/privalyse-mask-demo.gif"
