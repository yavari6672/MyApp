import paramiko

# Create SSH client
ssh = paramiko.SSHClient()

# Automatically add unknown host keys (for first-time connections)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Server connection details
hostname = "10.126.2.111"   # Server IP or domain
username = "root"           # SSH username
password = "Asdf@7890"  # SSH password

try:
    # Connect to the server
    ssh.connect(hostname, username=username, password=password)
    print("[+] Connected successfully to", hostname)

    # Execute a command on the server
    command = "ls -la"
    stdin, stdout, stderr = ssh.exec_command(command)

    # Read command output
    output = stdout.read().decode()
    error = stderr.read().decode()

    # Print output
    if output:
        print("=== Command Output ===")
        print(output)
    if error:
        print("=== Errors ===")
        print(error)

except Exception as e:
    print("[-] Connection failed:", str(e))

finally:
    # Close the connection
    ssh.close()
    print("[*] Connection closed.")
