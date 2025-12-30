#!/usr/bin/env python

import yaml
import argparse
import os
from tabulate import tabulate
import ipaddress

FILE_PATH = "servers.yaml"


def get_server(server):
    with open(FILE_PATH, "r") as s:
        try:
            return yaml.safe_load(s)[str(server)]
        except:
            return {}

# -------------------------
# Load data from YAML
# -------------------------


def load_data():
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        return data


# -------------------------
# Save data to YAML
# -------------------------
def save_data(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


# -------------------------
# Add new server
# -------------------------
def add_server(args):
    data = load_data()

    if args.name in data:
        print(f"❌ Entry '{args.name}' already exists!")
        return

    try:
        ipaddress.IPv4Address(args.host)
        data[args.name] = {
            "host": args.host,
            "protocol": args.protocol,
            "port": args.port,
            "user": args.user,
            "password": args.password,
            "full_access": 'yes' if args.full_access else 'no',
            "description": args.description
        }
        save_data(data)
        print(f"✅ '{args.name}' added successfully")
    except ipaddress.AddressValueError:
        print('❌ The IP address is not valid')


# -------------------------
# Update server
# -------------------------
def update_server(args):
    data = load_data()

    if args.name not in data:
        print(f"❌ Entry '{args.name}' not found!")
        return

    if args.host:
        try:
            ipaddress.IPv4Address(args.host)
        except ipaddress.AddressValueError:
            print('❌ The IP address is not valid')
            return

    entry = data[args.name]

    for field in ["host", "protocol", "port", "user", "password", "full_access", "description"]:
        value = getattr(args, field)
        if value is not None:
            entry[field] = value

    save_data(data)
    print(f"✅ '{args.name}' updated successfully")


# -------------------------
# Delete server
# -------------------------
def delete_server(args):
    data = load_data()

    if args.name not in data:
        print(f"❌ Entry '{args.name}' not found!")
        return

    del data[args.name]
    save_data(data)
    print(f"✅ '{args.name}' deleted successfully")


# -------------------------
# List servers (table output)
# -------------------------
def list_servers(args):
    data = load_data()

    if not data:
        print("📭 No servers found")
        return

    table = []

    for name, cfg in data.items():
        table.append([
            name,
            cfg.get("host"),
            cfg.get("protocol"),
            cfg.get("port"),
            cfg.get("user"),
            cfg.get("password"),
            cfg.get("full_access"),
            cfg.get("description")
        ])

    headers = ["Name", "Host", "Protocol",
               "Port", "User", "Password", "Full access", "Description"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


# -------------------------
# Main - argparse
# -------------------------


def main():
    parser = argparse.ArgumentParser(description="Server Manager")
    subparsers = parser.add_subparsers(dest="command")

    # add command
    add_p = subparsers.add_parser("add", help="Add new server")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--host", required=True)
    add_p.add_argument("--protocol", required=True)
    add_p.add_argument("--port", type=int, required=True)
    add_p.add_argument("--user", required=True)
    add_p.add_argument("--password", required=True)
    add_p.add_argument('-f', "--full_access",
                       action='store_true', help="Full access")
    add_p.add_argument("--description", default="")

    # update command
    upd_p = subparsers.add_parser("update", help="Update server")
    upd_p.add_argument("--name", required=True)
    upd_p.add_argument("--host")
    upd_p.add_argument("--protocol")
    upd_p.add_argument("--port", type=int)
    upd_p.add_argument("--user")
    upd_p.add_argument("--password")
    upd_p.add_argument('-f', "--full_access",
                       choices=['yes', 'no'], help="Full access")
    upd_p.add_argument("--description")

    # delete command
    del_p = subparsers.add_parser("delete", help="Delete server")
    del_p.add_argument("--name", required=True)

    # list command
    subparsers.add_parser("list", help="List all servers")

    args = parser.parse_args()

    if args.command == "add":
        add_server(args)
    elif args.command == "update":
        update_server(args)
    elif args.command == "delete":
        delete_server(args)
    elif args.command == "list":
        list_servers(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
