#!/usr/bin/env python
'''Managing SSH connections'''

import argparse
import paramiko
import sys
import os
import logging
import time
from datetime import datetime


class ssh:
    __number_connections = 0
    verbose = False


def setup_logger(logfile):
    logging.basicConfig(
        filename=os.path.dirname(os.path.abspath(
            __file__)) + r'/../log/'+logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("==== NEW SSH SESSION STARTED ====")


def ssh_connect(host, port, user, password, command, verbose):
    if not command:
        print('please enter cmd')
        return None
    try:
        logging.info(f"Connecting to {host}:{port} as {user}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password
        )

        logging.info(f"Connected successfully. Running command: {command}")

        # verbose
        time.sleep(3)
        vout = client.invoke_shell().recv(4096).decode()
        if verbose:
            logging.info("Command output:")
            logging.info(vout)

            print('Successful connection to server ', host)
            print(vout)

        print('Running command \"%s\"' % command)
        print('Please wait...')
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        logging.info("Command output:")
        logging.info(output)

        if error.strip():
            logging.error("Command error:")
            logging.error(error)

            print("Command error:")
            print(error)

        print(output)

        client.close()
        logging.info("Connection closed.")

    except Exception as e:
        logging.error(f"[ERROR] {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)


def interactive_ssh(host, port, user, password, command, verbose):
    try:
        logging.info(f"Connecting to {host}:{port} as {user}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password
        )
        channel = client.invoke_shell()

        time.sleep(2)
        vout = ""
        while channel.recv_ready():
            data = channel.recv(4096).decode()
            vout += data

        logging.info("Command output:")
        logging.info(vout)

        print('Successful connection to server ', host)
        print('To view the guide, please enter: myApp')
        print(vout, end='')

        if command:
            print(command)
            if command.lower() in ("exit", "quit"):
                logging.info("Session closed by user")
            else:
                channel.send((c := command + "\n"))
                logging.info(f"COMMAND: {command}")

                time.sleep(1)

                output = ""
                while channel.recv_ready():
                    data = channel.recv(4096).decode()
                    output += data

                print(output[len(c)+1:], end='')
                logging.info(f"OUTPUT:\n{output}")

        while True:
            command = input()

            if command.lower() in ("exit", "quit"):
                logging.info("Session closed by user")
                break

            channel.send((c := command + "\n"))
            logging.info(f"COMMAND: {command}")

            time.sleep(1)

            output = ""
            while channel.recv_ready():
                data = channel.recv(4096).decode()
                output += data

            print(output[len(c)+1:], end='')
            logging.info(f"OUTPUT:\n{output}")

        channel.close()
        client.close()

    except Exception as e:
        logging.error(f"ERROR: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SSH connect, run command, and write logs"
    )

    parser.add_argument('-H', "--host", required=True,
                        help="SSH IP address")
    parser.add_argument('-p', "--port", type=int, default=22,
                        help="SSH port (default 22)")
    parser.add_argument('-u', "--user", required=True, help="SSH username")
    parser.add_argument('-P', "--password", required=True, help="SSH password")
    parser.add_argument('-c', "--cmd",
                        help="Command to execute on server")
    parser.add_argument('-l', "--log", default=f"ssh_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                        help="Log file name")
    parser.add_argument('-i', '--interactive',
                        help='Interactive SSH', action="store_true")

    args = parser.parse_args()

    setup_logger(args.log)
    if args.interactive:
        interactive_ssh(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password, command=None, verbose=True
        )
    else:
        ssh_connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            command=args.cmd, verbose=True
        )
