#!/usr/bin/env python3
'''My Application'''
import argparse
import platform
import sys


def main():
    # Create the main argument parser
    parser = argparse.ArgumentParser(
        prog="MyApp",
        description=__doc__,
        epilog="Example: python myapp.py --sys"
    )

    # Add switches
    parser.add_argument('-s',
                        "--sys",
                        action="store_true",
                        help="show system information".capitalize()
                        )

    # Parse command-line arguments
    args = parser.parse_args()

    # Execute actions based on the switches
    if args.sys:
        print("Operating System: %s(%s)-%s(%s)" %
              (platform.system(), sys.getdefaultencoding().upper(), platform.version(), platform.machine()))
        print("Python Version:", sys.version)

    # If no switches are provided, show help message
    else:
        parser.print_help()


if __name__ == "__main__":
    print(__doc__.center(80, B := '-'))
    main()
    print(B*80)
