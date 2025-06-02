import subprocess

def run(*commands, cwd=None):
    """
    Führt eine Liste von Befehlen oder mehrere einzelne Befehle nacheinander aus
    und gibt die Ausgabe in Echtzeit auf der Konsole aus.

    Optional kann das Arbeitsverzeichnis mit cwd angegeben werden.

    Beispiele:
        run(["ls", "pwd"])
        run("ls", "pwd")
        run("ls", cwd="/tmp")
    """
    if len(commands) == 1 and isinstance(commands[0], list):
        cmds = commands[0]
    else:
        cmds = commands

    for cmd in cmds:
        print(f"[INFO] Führe aus: {cmd}")

        if isinstance(cmd, str):
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=cwd
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=cwd
            )

        for line in process.stdout:
            print(line, end='')

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
