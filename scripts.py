import os
import stat
import pwd
from tabulate import tabulate
from datetime import datetime


def get_list_scripts():
    scripts_path = os.path.dirname(os.path.abspath(__file__))+'/scripts'
    rows = []

    for e in os.scandir(scripts_path):
        st = e.stat()
        rows.append([
            e.name,
            stat.filemode(st.st_mode),
            pwd.getpwuid(st.st_uid).pw_name,
            datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "DIR" if e.is_dir() else "FILE"
        ])

    print(tabulate(
        rows,
        headers=["Name", "Permissions", "Owner",  "Modified", "Type"],
        tablefmt="fancy_grid"
    ))

    
