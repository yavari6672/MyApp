#!/usr/bin/env python
'''MyApp'''
import argparse
import servers
import scripts
from sys import version, platform, getdefaultencoding, exit
from connections import ssh
import ipaddress
from datetime import datetime


_App_version = "1.0.0"
_ID = id(__doc__)
_Baner = '''**************************************************************************
This app is designed to manage and monitor servers, devices, and networks.
**************************************************************************'''


def sysinfo():
    print('sysinfo'.upper().center(BS := 60, '-'))
    print("OS: %s(%s) \nPython version: %s" %
          (platform.capitalize(), getdefaultencoding().upper(), version))
    print("App version: {}".format(_App_version))
    print('-'*BS)


def main():
    """Main function of the program"""
    parser = argparse.ArgumentParser(__doc__)
    modes = parser.add_subparsers(dest='command', help='Program modes')

    # run mode
    run_mode = modes.add_parser('run', help='run mode')
    run_mode.add_argument(
        '-s', '--server', help='Server name or IP address', required=True)
    run_mode.add_argument(
        '-p', "--port", help="Server connection port for SSH protocol", required=False, default=22, type=int)
    run_mode.add_argument('-u', "--user", help="SSH username")
    run_mode.add_argument('-P', "--password",  help="SSH password")
    run_mode.add_argument('-c', "--cmd",
                          help="Command to execute on server")
    run_mode.add_argument('-i', '--interactive',
                          help='Interactive SSH', action="store_true")
    run_mode.add_argument('-v', "--verbose", action="store_true",
                          help="View complete and detailed information")
    run_mode.add_argument('-l', "--log", action="store_true",
                          help="Logging")

    # conf mode
    conf_mode = modes.add_parser('conf', help=' conf mode')
    conf_mode.add_argument(
        '-l', '--list', choices=['servers', 'scripts'], help='List of servers, scripts, etc')
    args = parser.parse_args()

    if args.command == 'run':
        if args.server:
            if args.verbose:
                sysinfo()
            if args.log:
                ssh.setup_logger(
                    f"ssh_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

            try:
                ipaddress.IPv4Address(args.server)
                if args.interactive:
                    ssh.interactive_ssh(args.server, args.port,
                                        args.user, args.password, args.cmd, args.verbose)
                else:
                    ssh.ssh_connect(args.server, args.port,
                                    args.user, args.password, args.cmd, args.verbose)

            except ipaddress.AddressValueError:
                server = servers.get_server(args.server)
                if args.interactive:
                    ssh.interactive_ssh(server['host'], server['port'],
                                        server['user'], server['password'], args.cmd, args.verbose)
                else:
                    ssh.ssh_connect(server['host'], server['port'],
                                    server['user'], server['password'], args.cmd, args.verbose)
            except Exception as err:
                print(err.__repr__())

    elif args.command == 'conf':
        if args.list:
            if args.list == 'servers':
                servers.list_servers(args)
            if args.list == 'scripts':
                scripts.get_list_scripts()
        else:
            parser.print_help()

    else:
        parser.print_help()


if __name__ == '__main__':
    print(_Baner)
    print(f'{__doc__} ID: {_ID} '.center(60, '-'))
    main()
    print(F"Goodbye! ID: {_ID} ".center(60, '-'))
