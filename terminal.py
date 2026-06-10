import os
import shlex
import subprocess

from commands import BUILTIN_COMMANDS, run_builtin


class Terminal:
    def __init__(self) -> None:
        self.current_dir = os.getcwd()
        self.history: list[str] = []

    @staticmethod
    def _tokenize(command_line: str) -> list[str]:
        lexer = shlex.shlex(command_line, posix=True, punctuation_chars="|<>")
        lexer.whitespace_split = True
        return list(lexer)

    @staticmethod
    def _has_shell_operators(tokens: list[str]) -> bool:
        for token in tokens:
            if token and set(token) <= {"|", "<", ">"} and any(char in token for char in "|<>"):
                return True
        return False

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

        try:
            if has_shell_operators:
                blocked_fragments = ("&&", "||", ";", "`", "$", "(", ")", "{", "}", "!")
                if any(fragment in command_line for fragment in blocked_fragments):
                    print("Unsupported shell expression for security reasons.")
                    return False

                completed = subprocess.run(
                    command_line,
                    shell=True,
                    cwd=self.current_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            else:
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
