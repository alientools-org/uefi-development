#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from time import sleep

from .utils import run

GIT_URL = "https://github.com/tianocore/edk2.git"


def parse_args():
    parser = argparse.ArgumentParser(description="EDK II Entwicklungsumgebung Setup Tool")
    parser.add_argument("-n", "--name", required=True, help="Name der Entwicklungsumgebung")
    parser.add_argument(
        "-a", "--arch", required=True, choices=["IA32", "X64", "ARM", "AARCH64"], help="Zielarchitektur"
    )
    parser.add_argument(
        "-b", "--build", required=True, help="Zu buildendes Paket oder 'all' für alles"
    )
    return parser.parse_args()


def git_clone_with_progress(repo_url: str, target_dir: Path):
    """
    Klont ein Git-Repository mit Fortschrittsanzeige.
    Wenn das Zielverzeichnis bereits existiert, wird der Klon übersprungen.
    """
    if target_dir.exists():
        print(f"[INFO] Zielverzeichnis '{target_dir}' existiert bereits. Klonen wird übersprungen.")
        return

    print(f"[INFO] Klone {repo_url} nach {target_dir} ...")

    process = subprocess.Popen(
        ["git", "clone", "--progress", repo_url, str(target_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    spinner = ['|', '/', '-', '\\']
    spin_idx = 0
    progress_regex = re.compile(r"Receiving objects:\s+(\d+)%")

    try:
        for line in process.stdout:
            line = line.strip()
            match = progress_regex.search(line)
            if match:
                percent = int(match.group(1))
                bar = ('█' * (percent // 2)).ljust(50)
                sys.stdout.write(f"\r[CLONE] [{bar}] {percent}%")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\r{spinner[spin_idx]} {line[:80]}")
                sys.stdout.flush()
                spin_idx = (spin_idx + 1) % len(spinner)
            sleep(0.02)  # optional für sanfte Darstellung

    except KeyboardInterrupt:
        process.kill()
        print("\n[ABBRUCH] Vorgang manuell abgebrochen.")
        sys.exit(1)

    process.wait()
    print("\n[INFO] Git-Clone abgeschlossen.")

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, ["git", "clone", repo_url, str(target_dir)])


def clone_edk2(target_dir: Path):
    if target_dir.exists():
        print(f"[INFO] Zielverzeichnis '{target_dir}' existiert bereits. Klonen wird übersprungen.")
        return

    print("[INFO] Klone EDK II Repository...")
    try:
        run(["git", "clone", GIT_URL, str(target_dir)])
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git-Clone fehlgeschlagen: {e}")
        print("[HINWEIS] Überprüfe die Netzwerkverbindung oder die Zielverzeichnisrechte.")
        sys.exit(1)

    print("[INFO] Initialisiere und aktualisiere Submodule...")
    try:
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=str(target_dir))
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Submodule-Update fehlgeschlagen: {e}")
        sys.exit(1)



def write_target_txt(edk_dir: Path, arch: str):
    conf_dir = edk_dir / "Conf"
    conf_dir.mkdir(parents=True, exist_ok=True)
    target_txt = conf_dir / "target.txt"
    with target_txt.open("w") as f:
        f.write(f"""ACTIVE_PLATFORM       = MdePkg/MdePkg.dsc
TARGET_ARCH           = {arch}
TOOL_CHAIN_TAG        = GCC5
BUILD_RULE_CONF       = $(EDK_TOOLS_PATH)/BuildRule/GccRules.mk
""")
    print(f"[INFO] target.txt geschrieben: {target_txt}")


def build_edk2(edk_dir: Path, build_target: str):
    edksetup = edk_dir / "edksetup.sh"
    if not edksetup.exists():
        print("[ERROR] edksetup.sh nicht gefunden!")
        sys.exit(1)

    print("[INFO] Setze Build-Umgebung auf...")

    # Shell-Befehl zusammenbauen
    if build_target.lower() == "all":
        build_cmd = "build"
    else:
        build_cmd = f"build -p MdePkg/MdePkg.dsc -m {build_target}"

    cmd = f"""
    cd {edk_dir} && \
    . ./edksetup.sh BaseTools && \
    make -C BaseTools && \
    {build_cmd}
    """

    print(f"[INFO] Starte Build mit: {build_cmd}")

    # Verwende subprocess direkt für vollständige Kontrolle (nicht run wrapper)
    process = subprocess.Popen(
        cmd,
        shell=True,
        executable="/bin/bash",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end='')

    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def main():
    args = parse_args()

    home = Path.home()
    workspace = home / args.name
    print(f"[INFO] Projektverzeichnis: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)

    os.chdir(workspace)
    print(f"[INFO] Arbeitsverzeichnis gewechselt zu: {workspace}")

    edk2_dir = workspace / "edk2"

    #clone_edk2(edk2_dir)
    git_clone_with_progress(GIT_URL, edk2_dir)
    write_target_txt(edk2_dir, args.arch)
    build_edk2(edk2_dir, args.build)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Fehler beim Ausführen: {e}")
        sys.exit(1)
