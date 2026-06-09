import json
import requests
import time
import os
import subprocess
import shlex
from typing import Dict

def execute_remote_command(command: str,
                           host: str = "eraigra-rpi",
                           user: str = "raimondo",
                           port: int = 22,
                           ) -> Dict[str, str]:
    """
    Executes a remote Linux command via SSH and returns structured output with dynamic message.
 
    Args:
        command: Shell command to be executed on the remote host.
        host: Remote host IP or hostname.
        user: SSH username.
        port: SSH port (default: 22)
 
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str,         # Description with command context
            "output": str           # stdout or stderr
        }
    """


    remote_command = shlex.quote(command)
    ssh_cmd = [
        "ssh", "-p", str(port),
        "-o", "ConnectTimeout=65",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "StrictHostKeyChecking=no",
        f"{user}@{host}",
        command
    ]

    print(f"[AGENT] Executing SSH Command:\n{' '.join(ssh_cmd)}")

    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True, timeout=900)
        output = result.stdout.strip()
        print(f"[AGENT] ✅ Remote command executed successfully: {command}")
        return {
            "status": "success",
            "message": f"The command '{remote_command}' executed successfully on remote host.",
            "output": output
        }

    except subprocess.TimeoutExpired as e:
        print(f"[AGENT] ⏱️ Command timed out: {command}")
        return {
            "status": "error",
            "message": f"The command '{remote_command}' timed out on remote host.",
            "output": str(e)
        }

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() or str(e)
        print(f"[AGENT] ❌ Remote command failed: {command}\nError: {error_output}")
        return {
            "status": "error",
            "message": f"The command '{remote_command}' failed on remote host.",
            "output": error_output
        }
