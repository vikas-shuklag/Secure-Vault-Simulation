#!/usr/bin/env python3
"""
Virtual HSM — Entry Point
Launches the Virtual HSM graphical dashboard.

Usage:
    python -m virtual_hsm.main
"""

from virtual_hsm.gui import start_gui


def main():
    start_gui()


if __name__ == "__main__":
    main()
