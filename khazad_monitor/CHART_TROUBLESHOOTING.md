# Chart Display Troubleshooting Guide

## If Charts Are Still Distorted

### 1. Terminal Size
Make sure your terminal window is large enough:
- **Minimum Width**: 100 characters
- **Minimum Height**: 30 lines

Check your terminal size:
```bash
echo "Columns: $(tput cols), Lines: $(tput lines)"
```

### 2. Font Issues
Some terminal fonts don't display Unicode properly. Try:
- **Recommended Fonts**:
  - Fira Code
  - JetBrains Mono
  - Source Code Pro
  - Consolas
  - Monaco

### 3. Terminal Settings
Ensure these settings in your terminal:
- **Character Encoding**: UTF-8
- **ANSI Colors**: Enabled
- **256 Color Support**: Enabled

### 4. Plotext Configuration
If black background doesn't work, try manual configuration:

```python
# In cyberpunk_charts.py, add these lines after plt.theme('dark'):
import os
os.environ['PLOTEXT_DARK_THEME'] = '1'
plt.limit_size(False)  # Allow full terminal usage
plt.colorless(False)   # Ensure colors are enabled
```

### 5. Alternative Markers
If the 'braille' markers cause issues, change them:

```python
# Replace marker='braille' with:
marker='dot'     # Simple dots
marker='hd'      # Horizontal dashes
marker='square'  # Square blocks
```

### 6. Terminal-Specific Fixes

#### For Windows Terminal:
- Settings → Profiles → Defaults → Appearance → Color Scheme: "One Half Dark"

#### For iTerm2 (Mac):
- Preferences → Profiles → Colors → Color Presets: "Dark Background"

#### For Linux (GNOME Terminal):
- Preferences → Profiles → Colors → Built-in schemes: "Black on white"
- Then invert colors

### 7. Force Black Background in Terminal
If plotext can't override your terminal's background:

```bash
# Add to your .bashrc or .zshrc:
export TERM=xterm-256color

# Or run before launching:
TERM=xterm-256color python cyberpunk_monitor.py
```

### 8. Test with Simple Plot
Run the test script to verify basic functionality:
```bash
python test_charts.py
```

### 9. Fallback Option
If charts still don't work properly, use the simple monitor:
```bash
python simple_monitor.py
```

This version has less complex charts that work in more terminals.

## Common Issues and Solutions

### Issue: Charts appear compressed
**Solution**: Increase terminal width or reduce chart width in config:
```python
# In cyberpunk_charts.py
plt.plotsize(60, 15)  # Reduce from 80, 20
```

### Issue: Lines don't align
**Solution**: Disable line wrapping in terminal settings

### Issue: Colors don't show
**Solution**: Check TERM environment variable:
```bash
echo $TERM  # Should show xterm-256color or similar
```

### Issue: Background stays white/gray
**Solution**: Your terminal might override background colors. Try:
1. Change terminal theme to a dark theme
2. Use a different terminal emulator
3. Manually set background in terminal preferences

## Testing Colors
Run this to test your terminal's color support:
```bash
for i in {0..255}; do
    printf "\x1b[48;5;%sm%3d\e[0m " "$i" "$i"
    if (( i == 15 )) || (( i > 15 )) && (( (i-15) % 16 == 0 )); then
        echo
    fi
done
```

If you see 256 colored blocks, your terminal supports full colors.
