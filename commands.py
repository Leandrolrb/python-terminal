import os
import subprocess
from typing import Any


BUILTIN_COMMANDS = {"cd", "pwd", "exit", "quit", "help", "clear", "history"}


def _help_text() -> str:
    return (
        "Built-in commands:\n"
        "  cd [dir]   Change current directory\n"
        "  pwd        Print current directory\n"
        "  clear      Clear the terminal screen\n"
        "  help       Show this help message\n"
        "  history    Show command history for this session\n"
        "  exit|quit  Exit the terminal"
    )


def run_builtin(command: str, args: list[str], current_dir: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exit": False,
        "new_dir": current_dir,
        "output": "",
        "error": "",
    }

    if command in {"exit", "quit"}:
        result["exit"] = True
        return result

    if command == "pwd":
        result["output"] = current_dir
        return result

    if command == "help":
        result["output"] = _help_text()
        return result

    if command == "clear":
        if os.name == "nt":
            try:
                subprocess.run(["cmd", "/c", "cls"], check=False)
            except OSError as error:
                result["error"] = f"clear: {error}"
        else:
            print("\033[2J\033[H", end="")
        return result

    if command == "cd":
        target = args[0] if args else os.path.expanduser("~")
        target_path = target if os.path.isabs(target) else os.path.join(current_dir, target)
        target_path = os.path.abspath(os.path.expanduser(target_path))

        if not os.path.isdir(target_path):
            result["error"] = f"cd: no such directory: {target}"
            return result

        result["new_dir"] = target_path
        return result

    if command == "history":
        return result

    return result
