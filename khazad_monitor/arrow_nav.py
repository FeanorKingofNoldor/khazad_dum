#!/usr/bin/env python3
"""
Arrow Navigation Helper for Cyberpunk Monitor
Handles keyboard input without external dependencies
"""

import sys
import os
import termios
import tty
import select
from typing import List, Tuple, Optional


class ArrowNavigator:
    """Simple arrow key navigation handler"""
    
    # Key codes
    KEY_UP = '\x1b[A'
    KEY_DOWN = '\x1b[B'
    KEY_RIGHT = '\x1b[C'
    KEY_LEFT = '\x1b[D'
    KEY_ENTER = '\r'
    KEY_SPACE = ' '
    KEY_ESCAPE = '\x1b'
    
    def __init__(self):
        self.original_settings = None
        
    def setup_terminal(self):
        """Set terminal to raw mode for key capture"""
        if sys.platform != 'win32':
            self.original_settings = termios.tcgetattr(sys.stdin)
            
    def restore_terminal(self):
        """Restore terminal to original settings"""
        if sys.platform != 'win32' and self.original_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_settings)
    
    def get_key(self) -> str:
        """Get a single keypress"""
        if sys.platform == 'win32':
            # Windows handling (simplified)
            import msvcrt
            key = msvcrt.getch()
            if key in [b'\xe0', b'\000']:
                key = msvcrt.getch()
                key_map = {
                    b'H': self.KEY_UP,
                    b'P': self.KEY_DOWN,
                    b'K': self.KEY_LEFT,
                    b'M': self.KEY_RIGHT,
                }
                return key_map.get(key, '')
            return key.decode('utf-8', errors='ignore')
        else:
            # Unix/Linux handling
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                
                # Read first character
                key = sys.stdin.read(1)
                
                # Check for escape sequences (arrow keys)
                if key == '\x1b':
                    # Check if more characters are available
                    if select.select([sys.stdin], [], [], 0)[0]:
                        key += sys.stdin.read(2)
                
                return key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def navigate_menu(self, items: List[str], title: str = "Menu", 
                     allow_multi: bool = False) -> Optional[int]:
        """
        Navigate a menu with arrow keys
        
        Args:
            items: List of menu items
            title: Menu title
            allow_multi: Allow multiple selection (not implemented yet)
            
        Returns:
            Selected index or None if cancelled
        """
        selected = 0
        
        while True:
            # Clear screen
            os.system('clear' if os.name != 'nt' else 'cls')
            
            # Display menu
            print(f"\n{title}")
            print("=" * len(title))
            print()
            
            for i, item in enumerate(items):
                if i == selected:
                    print(f"  ► {item} ◄")
                else:
                    print(f"    {item}")
            
            print()
            print("─" * 40)
            print("[↑↓] Navigate  [Enter] Select  [Q] Quit")
            
            # Get key
            key = self.get_key()
            
            if key == self.KEY_UP:
                selected = (selected - 1) % len(items)
            elif key == self.KEY_DOWN:
                selected = (selected + 1) % len(items)
            elif key == self.KEY_ENTER:
                return selected
            elif key.lower() == 'q':
                return None


class SimpleMenu:
    """Simple menu system with cyberpunk styling"""
    
    def __init__(self, console):
        self.console = console
        self.navigator = ArrowNavigator()
        
    def show_menu(self, title: str, options: List[Tuple[str, callable]]) -> None:
        """
        Show a menu and execute selected option
        
        Args:
            title: Menu title
            options: List of (label, function) tuples
        """
        labels = [opt[0] for opt in options]
        selected = self.navigator.navigate_menu(labels, title)
        
        if selected is not None and selected < len(options):
            # Execute the selected function
            options[selected][1]()
