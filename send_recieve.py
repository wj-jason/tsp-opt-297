import paramiko 
from paramiko import Ed25519Key
import os
import time
import socket


SERVER_IP = "ug135.eecg.toronto.edu"
SERVER_PORT = 22
USERNAME = "wangja58"
KEY_PATH = Ed25519Key.from_private_key_file(os.path.expanduser("~/.ssh/id_ed25519"))

def send_file(local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_IP, SERVER_PORT, USERNAME, pkey=KEY_PATH)
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        print(f"Sent {local_path} to {remote_path}")
        sftp.close()
    finally:
        ssh.close()

def await_file(remote_path, local_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.load_system_host_keys()
    try:
        ssh.connect(SERVER_IP, SERVER_PORT, USERNAME, pkey=KEY_PATH)
        sftp = ssh.open_sftp()
        print(f"Waiting for {remote_path}")
        while True:
            try:
                sftp.stat(remote_path)
                print(f"{remote_path} found. Downloading...")
                sftp.get(remote_path, local_path)
                print(f"Downloaded to {local_path}")
                break
            except FileNotFoundError:
                pass
        sftp.close()
    finally:
        ssh.close()


def send_continue():
    remote_path = "/nfs/ug/homes-4/w/wangja58/ece297/work/mapper/optimizer/"
    send_file("continue", remote_path + "external/continue")

# def check_continue():
#     remote_path = "/nfs/ug/homes-4/w/wangja58/ece297/work/mapper/optimizer/external/continue"

#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     cont_exists = True
#     try:
#         ssh.connect(SERVER_IP, SERVER_PORT, USERNAME, pkey=KEY_PATH)
#         sftp = ssh.open_sftp()
#         try:
#             sftp.stat(remote_path)
#             cont_exists = True
#         except FileNotFoundError:
#             cont_exists = False
#         sftp.close()
#     finally:
#         ssh.close()

#     return cont_exists

def check_continue(retry_delay=5):
    remote_path = "/nfs/ug/homes-4/w/wangja58/ece297/work/mapper/optimizer/external/continue"

    """Continuously tries to establish an SSH connection and check for a remote file, retrying on failure indefinitely."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    while True:  # Infinite loop for unlimited retries
        try:
            ssh.connect(SERVER_IP, SERVER_PORT, USERNAME, pkey=KEY_PATH)
            sftp = ssh.open_sftp()
            try:
                sftp.stat(remote_path)  # Check if file exists
                cont_exists = True
            except FileNotFoundError:
                cont_exists = False
            sftp.close()
            ssh.close()
            return cont_exists  # Successfully checked, return result

        except (socket.timeout, paramiko.SSHException) as e:
            print(f"SSH connection failed: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying

        finally:
            ssh.close()
