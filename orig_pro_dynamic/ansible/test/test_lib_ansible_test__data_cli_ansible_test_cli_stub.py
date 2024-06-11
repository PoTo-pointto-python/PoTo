"""Command line entry point for ansible-test."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import sys

def main():
    """Main program entry point."""
    ansible_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_root = os.path.join(ansible_root, 'test', 'lib')
    if os.path.exists(os.path.join(source_root, 'ansible_test', '_internal', 'cli.py')):
        sys.path.insert(0, source_root)
    from ansible_test._internal.cli import main as cli_main
    cli_main()
if __name__ == '__main__':
    main()