"""
KHAZAD_DUM Cyberpunk Theme Configuration
"""

# Cyberpunk color palette
COLORS = {
    # Main UI colors
    'primary': 'bright_cyan',      # Neon cyan
    'secondary': 'bright_magenta',  # Hot magenta
    'accent': 'bright_green',       # Matrix green
    'warning': 'bright_yellow',     # Warning yellow
    'danger': 'bright_red',         # Blood red
    'dark': 'grey23',               # Dark background
    'light': 'grey85',              # Light text
    
    # Chart colors
    'price_line': 'cyan',
    'stop_loss': 'red',
    'target': 'green',
    'current': 'yellow',
    'portfolio': 'magenta',
    'entry': 'white',
    
    # Status colors
    'profit': 'bright_green',
    'loss': 'bright_red',
    'neutral': 'grey50',
    
    # ASCII art gradient
    'gradient': ['grey23', 'grey35', 'grey46', 'cyan', 'bright_cyan'],
}

# ASCII Art Headers
ASCII_ART = {
    'logo': """
╔═══════════════════════════════════════════════════════════════════════╗
║  ██╗  ██╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗     ██████╗ ██╗   ██╗███╗   ███╗ ║
║  ██║ ██╔╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗    ██╔══██╗██║   ██║████╗ ████║ ║
║  █████╔╝ ███████║███████║  ███╔╝ ███████║██║  ██║    ██║  ██║██║   ██║██╔████╔██║ ║
║  ██╔═██╗ ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║    ██║  ██║██║   ██║██║╚██╔╝██║ ║
║  ██║  ██╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝    ██████╔╝╚██████╔╝██║ ╚═╝ ██║ ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝     ╚═════╝  ╚═════╝ ╚═╝     ╚═╝ ║
╚═══════════════════════════════════════════════════════════════════════╝
    """,
    
    'skull': """
      ▄▄▄▄▄▄▄▄▄▄▄▄▄
     ▀▀▀██████▄▄▄
   ▄▄▄▄▄█████████▄
   ▀▀▀▀█████▌
 ▄▄▄▄▄▄▀████▌
 ▀▀██████▄██
   ▀▄▄▄▄▄█▌
      ▀▀▀▀▀
    """,
    
    'matrix': """
    01001011 01001000 01000001 01011010 01000001 01000100
    ╔════════════════════════════════════════════╗
    ║  ░▒▓█ SYSTEM INITIALIZED █▓▒░             ║
    ╚════════════════════════════════════════════╝
    """
}

# Menu icons
ICONS = {
    'portfolio': '📊',
    'position': '📈',
    'table': '📋',
    'files': '💾',
    'command': '⌨️',
    'refresh': '🔄',
    'settings': '⚙️',
    'quit': '🚪',
    'up': '▲',
    'down': '▼',
    'right': '▶',
    'left': '◀',
    'folder': '📁',
    'file': '📄',
    'download': '⬇️',
    'upload': '⬆️',
}

# Cyberpunk style box characters
BOX = {
    'double': {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║', 't': '╦', 'b': '╩',
        'l': '╠', 'r': '╣', 'x': '╬'
    },
    'single': {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│', 't': '┬', 'b': '┴',
        'l': '├', 'r': '┤', 'x': '┼'
    },
    'heavy': {
        'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
        'h': '━', 'v': '┃', 't': '┳', 'b': '┻',
        'l': '┣', 'r': '┫', 'x': '╋'
    }
}
