"""
This is the main module for gui-driven execution of paws.
"""

import sys

from paws.qt.widgets import widget_launcher

def main():
    """
    Main entry point for paws with a gui.
    """
    widget_launcher.main()   
 
# Run the main() function if this module is invoked 
if __name__ == '__main__':
    main()

