import os
import shlex
import subprocess
from pathlib import Path

from commands import BUILTIN_COMMANDS, run_builtin


class Terminal:
    def __init__(self) -> None:
        self.current_dir = os.getcwd()
        self.history: list[str] = []

    @staticmethod
    def _tokenize(command_line: str) -> list[str]:
        lexer = shlex.shlex(command_line, posix=True, punctuation_chars="|<>")
        return list(lexer)

    @staticmethod
    def _has_shell_operators(tokens: list[str]) -> bool:
        for token in tokens:
            if token and set(token) <= {"|", "<", ">"}:
                return True
        return False

    def _run_pipeline(self, tokens: list[str]) -> None:
        commands: list[list[str]] = []
        current: list[str] = []
        input_file: str | None = None
        output_file: str | None = None
        append_output = False

        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "|":
                if not current:
                    print("Invalid pipeline syntax.")
                    return
                commands.append(current)
                current = []
            elif token in {"<", ">", ">>"}:
                if index + 1 >= len(tokens):
                    print(f"Missing path after {token}")
                    return

                path_token = tokens[index + 1]
                index += 1
                if token == "<":
                    input_file = path_token
                else:
                    output_file = path_token
                    append_output = token == ">>"
            else:
                current.append(token)
            index += 1

        if current:
            commands.append(current)

        if not commands:
            print("No command to execute.")
            return

        input_data: str | None = None
        if input_file:
            input_path = Path(self.current_dir) / input_file
            try:
                input_data = input_path.read_text()
            except OSError as error:
                print(f"Input redirection error: {error}")
                return

        for command_parts in commands:
            try:
                completed = subprocess.run(
                    command_parts,
                    shell=False,
                    cwd=self.current_dir,
                    input=input_data,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except OSError as error:
                print(f"Execution error: {error}")
                return

            if completed.stderr:
                print(completed.stderr, end="")
            if completed.returncode != 0:
                if not completed.stderr:
                    print(f"Command failed with exit code {completed.returncode}")
                return

            input_data = completed.stdout

        output_text = input_data or ""
        if output_file:
            output_path = Path(self.current_dir) / output_file
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                mode = "a" if append_output else "w"
                with output_path.open(mode) as file_handle:
                    file_handle.write(output_text)
            except OSError as error:
                print(f"Output redirection error: {error}")
        elif output_text:
            print(output_text, end="")

    def _run_command(self, command_line: str) -> bool:
        try:
            tokens = self._tokenize(command_line)
        except ValueError as error:
            print(f"Parse error: {error}")
            return False

        if not tokens:
            return False

        has_shell_operators = self._has_shell_operators(tokens)

        if not has_shell_operators:
            command, args = tokens[0], tokens[1:]
            if command in BUILTIN_COMMANDS:
                if command == "history":
                    for index, entry in enumerate(self.history, start=1):
                        print(f"{index}: {entry}")
                    return False

                result = run_builtin(command, args, self.current_dir)
                self.current_dir = result["new_dir"]

                if result["output"]:
                    print(result["output"])
                if result["error"]:
                    print(result["error"])

                return result["exit"]

        if has_shell_operators:
            self._run_pipeline(tokens)
            return False

        try:
            completed = subprocess.run(
                tokens,
                shell=False,
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as error:
            print(f"Execution error: {error}")
            return False

        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="")
        if completed.returncode != 0 and not completed.stderr:
            print(f"Command failed with exit code {completed.returncode}")

        return False

    def run(self) -> None:
        while True:
            try:
                command_line = input(f"{self.current_dir} $ ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not command_line:
                continue

            self.history.append(command_line)

            if self._run_command(command_line):
                break
