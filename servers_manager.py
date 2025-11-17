#!/usr/bin/env python3
"""
servers_manager.py

A simple CLI tool to manage server information in a YAML file.

Commands:
  add     - Add a new server
  list    - List all servers (table or JSON)
  remove  - Remove a server by name or IP
  update  - Update an existing server

Examples:
  python servers_manager.py add --name web1 --ip 192.168.1.10 --user admin --protocol ssh --env prod
  python servers_manager.py list
  python servers_manager.py remove --name web1
  python servers_manager.py update --name db1 --port 3307
  python servers_manager.py list --json
"""

import argparse
import getpass
import os
import sys
import json
from typing import List, Dict, Any

try:
    import yaml
    from tabulate import tabulate
except ImportError:
    print("Please install dependencies:\n  pip install pyyaml tabulate")
    sys.exit(1)

DEFAULT_FILE = "servers.yml"

DEFAULT_PROTOCOL_PORT = {
    "ssh": 22,
    "telnet": 23,
    "http": 80,
    "https": 443,
    "rdp": 3389,
    "mysql": 3306,
    "postgres": 5432,
}


def load_servers(path: str) -> List[Dict[str, Any]]:
    """Load servers from YAML file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, list) else []


def save_servers(path: str, servers: List[Dict[str, Any]]) -> None:
    """Save servers list to YAML."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(servers, f, sort_keys=False, allow_unicode=True)


def infer_port(protocol: str, port: int | None) -> int | None:
    """Get default port based on protocol."""
    return port if port is not None else DEFAULT_PROTOCOL_PORT.get(protocol.lower())


def add_server(path: str, name: str, ip: str, user: str, password: str,
               tag: str | None, port: int | None, env: str, protocol: str) -> None:
    """Add a new server to the list."""
    servers = load_servers(path)

    # Prevent duplicates
    for s in servers:
        if s.get("name") == name:
            print(f"Server '{name}' already exists.")
            return
        if s.get("ip") == ip:
            print(f"Server with IP '{ip}' already exists.")
            return

    servers.append({
        "name": name,
        "ip": ip,
        "user": user,
        "password": password,
        "tag": tag or "",
        "port": infer_port(protocol, port),
        "env": env,
        "protocol": protocol.lower(),
    })

    save_servers(path, servers)
    print(f"✅ Server '{name}' added successfully.")


def list_servers(path: str, as_json: bool = False) -> None:
    """Display servers as table or JSON."""
    servers = load_servers(path)
    if not servers:
        print("No servers found.")
        return

    if as_json:
        print(json.dumps(servers, indent=2, ensure_ascii=False))
        return

    headers = ["Name", "IP", "Port", "User", "Protocol", "Env", "Tag"]
    table = [[s.get("name"), s.get("ip"), s.get("port"), s.get("user"),
              s.get("protocol"), s.get("env"), s.get("tag")] for s in servers]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def remove_server(path: str, name: str | None, ip: str | None) -> None:
    """Remove a server by name or IP."""
    servers = load_servers(path)
    if not servers:
        print("Server list is empty.")
        return

    new_list = []
    removed = False
    for s in servers:
        if (name and s.get("name") == name) or (ip and s.get("ip") == ip):
            removed = True
            continue
        new_list.append(s)

    if not removed:
        print("⚠ No matching server found.")
    else:
        save_servers(path, new_list)
        print("🗑 Server removed successfully.")


def update_server(path: str, name: str, updates: Dict[str, Any]) -> None:
    """Update server fields by name."""
    servers = load_servers(path)
    for s in servers:
        if s.get("name") == name:
            s.update({k: v for k, v in updates.items() if v is not None})
            save_servers(path, servers)
            print(f"🔄 Server '{name}' updated successfully.")
            return
    print(f"⚠ Server '{name}' not found.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage server list (stored in YAML)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Add ---
    add_p = subparsers.add_parser("add", help="Add a server")
    add_p.add_argument("--name", "-n", required=True)
    add_p.add_argument("--ip", "-i", required=True)
    add_p.add_argument("--user", "-u", required=True)
    add_p.add_argument("--password", "-p")
    add_p.add_argument("--tag", "-t")
    add_p.add_argument("--port", type=int)
    add_p.add_argument("--env", choices=["prod", "dev"], default="prod")
    add_p.add_argument(
        "--protocol", choices=list(DEFAULT_PROTOCOL_PORT.keys()), default="ssh")
    add_p.add_argument("--file", "-f", default=DEFAULT_FILE)

    # --- List ---
    list_p = subparsers.add_parser("list", help="List servers")
    list_p.add_argument("--file", "-f", default=DEFAULT_FILE)
    list_p.add_argument("--json", action="store_true", help="Display as JSON")

    # --- Remove ---
    rem_p = subparsers.add_parser(
        "remove", help="Remove a server by name or IP")
    rem_p.add_argument("--name", "-n")
    rem_p.add_argument("--ip", "-i")
    rem_p.add_argument("--file", "-f", default=DEFAULT_FILE)

    # --- Update ---
    upd_p = subparsers.add_parser(
        "update", help="Update server fields by name")
    upd_p.add_argument("--name", "-n", required=True,
                       help="Server name to update")
    upd_p.add_argument("--ip", "-i")
    upd_p.add_argument("--user", "-u")
    upd_p.add_argument("--password", "-p")
    upd_p.add_argument("--tag", "-t")
    upd_p.add_argument("--port", type=int)
    upd_p.add_argument("--env", choices=["prod", "dev"])
    upd_p.add_argument(
        "--protocol", choices=list(DEFAULT_PROTOCOL_PORT.keys()))
    upd_p.add_argument("--file", "-f", default=DEFAULT_FILE)

    args = parser.parse_args()

    # Command handling
    if args.command == "add":
        password = args.password or getpass.getpass("Password: ")
        add_server(args.file, args.name, args.ip, args.user,
                   password, args.tag, args.port, args.env, args.protocol)

    elif args.command == "list":
        list_servers(args.file, args.json)

    elif args.command == "remove":
        if not args.name and not args.ip:
            print("You must specify --name or --ip to remove.")
            return
        remove_server(args.file, args.name, args.ip)

    elif args.command == "update":
        updates = {
            "ip": args.ip,
            "user": args.user,
            "password": args.password,
            "tag": args.tag,
            "port": args.port,
            "env": args.env,
            "protocol": args.protocol,
        }
        update_server(args.file, args.name, updates)


if __name__ == "__main__":
    main()
