#!/usr/bin/env python3
"""
KHAZAD_DUM Cyberpunk Launcher
Runs the improved cyberpunk monitor
"""

import os
import sys

# ASCII art startup
BOOT_SEQUENCE = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     ██╗███╗   ██╗██╗████████╗██╗ █████╗ ██╗     ██╗███████╗      ║
║     ██║████╗  ██║██║╚══██╔══╝██║██╔══██╗██║     ██║╚══███╔╝      ║
║     ██║██╔██╗ ██║██║   ██║   ██║███████║██║     ██║  ███╔╝       ║
║     ██║██║╚██╗██║██║   ██║   ██║██╔══██║██║     ██║ ███╔╝        ║
║     ██║██║ ╚████║██║   ██║   ██║██║  ██║███████╗██║███████╗      ║
║     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝      ║
║                                                                    ║
║                    [SYSTEM BOOT SEQUENCE]                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""

def main():
    # Clear screen
    os.system('clear' if os.name != 'nt' else 'cls')
    
    # Show boot sequence
    print("\033[1;36m" + BOOT_SEQUENCE + "\033[0m")
    
    print("\033[1;32m[+] Loading KHAZAD_DUM Core...\033[0m")
    
    try:
        # Try to import required modules
        import rich
        print("\033[1;32m[✓] Rich UI loaded\033[0m")
        
        import plotext
        print("\033[1;32m[✓] Chart engine loaded\033[0m")
        
        from cyberpunk_theme import COLORS
        print("\033[1;32m[✓] Cyberpunk theme loaded\033[0m")
        
    except ImportError as e:
        print(f"\033[1;31m[✗] Missing dependency: {e}\033[0m")
        print("\033[1;33m[!] Installing dependencies...\033[0m")
        os.system("pip install -r requirements.txt --break-system-packages --quiet")
    
    print("\n\033[1;35m◢◤ SELECT INTERFACE ◢◤\033[0m\n")
    print("  \033[1;36m[1]\033[0m Cyberpunk Monitor (Advanced)")
    print("  \033[1;36m[2]\033[0m Simple Monitor (Basic)")
    print("  \033[1;36m[3]\033[0m Test System")
    print("  \033[1;36m[4]\033[0m Exit")
    
    try:
        choice = input("\n\033[1;35m◢◤ SELECT> \033[0m")
        
        if choice == "1":
            print("\033[1;32m[+] Launching Cyberpunk Interface...\033[0m")
            from cyberpunk_monitor import CyberpunkMonitor
            monitor = CyberpunkMonitor()
            monitor.run()
        elif choice == "2":
            print("\033[1;32m[+] Launching Simple Interface...\033[0m")
            from simple_monitor import SimpleMonitor
            monitor = SimpleMonitor()
            monitor.run()
        elif choice == "3":
            print("\033[1;32m[+] Running system tests...\033[0m")
            os.system("python test_monitor.py")
        else:
            print("\033[1;31m◢◤ SYSTEM SHUTDOWN ◢◤\033[0m")
            
    except KeyboardInterrupt:
        print("\n\033[1;31m◢◤ EMERGENCY SHUTDOWN ◢◤\033[0m")
    except Exception as e:
        print(f"\n\033[1;31m[!] System Error: {e}\033[0m")


if __name__ == "__main__":
    main()
