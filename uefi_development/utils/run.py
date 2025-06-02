import subprocess
import sys

def run(*commands):
    """
    Führt eine Liste von Befehlen oder mehrere einzelne Befehle nacheinander aus
    und gibt die Ausgabe in Echtzeit auf der Konsole aus.

    Beispiele:
        run_commands(["ls", "pwd"])
        run_commands("ls", "pwd")
    """
    if len(commands) == 1 and isinstance(commands[0], list):
        cmds = commands[0]
    else:
        cmds = commands

    for cmd in cmds:
        print(f"[INFO] Führe aus: {cmd}")

        # Für String-Kommandos (Shell) vs Listen-Kommandos
        if isinstance(cmd, str):
            process = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

        # Echtzeit-Ausgabe der Zeilen
        for line in process.stdout:
            print(line, end='')

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
