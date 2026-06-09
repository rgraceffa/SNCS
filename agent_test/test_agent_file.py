from gradio_client import Client, handle_file
import sys
import time

AGENT_CONTEXT = """
You are a Linux system administrator AI agent operating on a Linux system or issuing commands remotely over SSH. Your goal is to output or execute only valid, safe Linux shell commands for diagnostics, monitoring, and system management.

Rules:

1. Use only default Linux utilities (e.g., ip, ss, ps, ls, cat, echo, grep, awk, sed, df, du, top, free, uptime, journalctl).
2. When creating or writing to files:
   - To create or overwrite: echo "text" > filename
   - To append: echo "text" >> filename
3. For multi-line files:
   - When running locally, you may use a here-document (<<) safely:
     cat <<'EOF' > filename
     (file contents)
     EOF
   - When running over SSH, use:
     echo -e 'line1\nline2\nline3' > filename
     and escape all special characters ($, ", (), \) correctly.
4. Always wrap literal text in single quotes ('') unless variable substitution is required.
   - Inside SSH commands, wrap the entire remote command in double quotes ("") and escape inner characters as needed.
   - Example:
     ssh user@host "echo -e '#!/bin/bash\nName=\$1\necho \"Hello \$Name\"' > /home/user/script.sh"
5. Always validate shell syntax and quoting so the command can be copied and executed directly in Bash without errors.
6. Use logical operators (&& or ||) to chain commands safely.
7. Output only valid shell commands — no explanations, pseudocode, or commentary.
8. Use sudo only when the operation requires root privileges.
9. Avoid destructive or high-risk commands (e.g., rm -rf, mkfs, dd) unless explicitly instructed.
10. When echoing text with variables or quotes inside, ensure correct escaping so variables are not expanded locally before reaching the remote shell.
11. Assume the remote shell is Bash-compatible unless stated otherwise.
12. All commands must be syntactically valid for execution directly in a Linux terminal or inside an SSH call.

"""

def run_stage(client: Client, stage_name: str, task_text: str, retries: int = 1, delay: int = 3) -> bool:
    """
    Runs one stage (preexec, command, verify, postexec).
    Retries up to `retries` times if not successful.
    Returns True if successful, False otherwise.
    """
    if not task_text.strip():
        print(f"[{stage_name}] ⚠️ Empty — skipping.")
        return True  # Empty means skip but continue

    print(f"\n[{stage_name}] ▶️ Executing: {task_text}\n")

    for attempt in range(1, retries + 1):
        try:
            result = client.predict(
                message=task_text,
                mode="xAgent",
                param_3=[handle_file("loadfile.txt")],
                param_4=AGENT_CONTEXT,
                api_name="/chat",
            )
        except Exception as e:
            print(f"[{stage_name}] ❌ Error contacting Gradio backend: {e}")
            return False

        print(f"[{stage_name}] Attempt {attempt} Result:\n{result}\n")

        # Detect success
        if isinstance(result, str):
            success = "success" in result.lower()
        elif isinstance(result, dict):
            success = "success" in str(result).lower()
        else:
            success = False

        if success:
            print(f"[{stage_name}] ✅ Success detected on attempt {attempt}. Continuing...\n")
            return True

        if attempt < retries:
            print(f"[{stage_name}] 🔁 Retry {attempt}/{retries} failed. Retrying in {delay}s...\n")
            time.sleep(delay)

    print(f"[{stage_name}] ❌ Failed after {retries} attempts.\n")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: test_agent_file.py /path/to/file")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        print(f"Error: file '{file_path}' not found.")
        sys.exit(1)

    if len(lines) < 5:
        print(f"Error: {file_path} has less than 5 valid lines.")
        sys.exit(1)

    # Extract tasks
    task_preexecution = lines[1].split("=", 1)[1].strip()
    task_command = lines[2].split("=", 1)[1].strip()
    task_verify = lines[3].split("=", 1)[1].strip()
    task_postexecution = lines[4].split("=", 1)[1].strip()

    client = Client("http://127.0.0.1:8002/")

    print(f"\n🚀 Starting 4-Stage Execution Pipeline for: {file_path}\n")

    # Stage 1: Pre-Execution
    if not run_stage(client, "PRE-EXECUTION", task_preexecution):
        print("\n⛔ Stopping at PRE-EXECUTION.\n")
        sys.exit(1)

    # Stage 2: Command (up to 5 retries)
    if not run_stage(client, "COMMAND", task_command, retries=5, delay=5):
        print("\n⛔ Stopping at COMMAND stage after max retries.\n")
        sys.exit(1)

    # Stage 3: Verify
    if not run_stage(client, "VERIFY", task_verify):
        print("\n⛔ Stopping at VERIFY.\n")
        sys.exit(1)

    # Stage 4: Post-Execution
    if not run_stage(client, "POST-EXECUTION", task_postexecution):
        print("\n⛔ Stopping at POST-EXECUTION.\n")
        sys.exit(1)

    print("\n✅ All stages completed successfully!\n")


if __name__ == "__main__":
    main()
