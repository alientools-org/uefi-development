#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

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


def clone_edk2(target_dir: Path):
    if target_dir.exists():
        print(f"[INFO] Zielverzeichnis '{target_dir}' existiert bereits. Klonen wird übersprungen.")
        return

    print("[INFO] Klone EDK II Repository...")
    run(["git", "clone", GIT_URL, str(target_dir)])

    print("[INFO] Initialisiere und aktualisiere Submodule...")
    run(["git", "pull"], cwd=str(target_dir))
    run(["git", "submodule", "update", "--init", "--recursive"], cwd=str(target_dir))
    run(["git", "pull"], cwd=str(target_dir))


def build(target_dir: Path):
    print("Building Packages !!!")
    run(["build"], cwd=str(target_dir))

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

    commands = [
        f"cd {edk_dir}",
        ". ./edksetup.sh BaseTools",
        "make -C BaseTools"
    ]

    if build_target.lower() == "all":
        commands.append("build")
    else:
        commands.append(f"build -p MdePkg/MdePkg.dsc -m {build_target}")

    full_cmd = " && ".join(commands)
    print(f"[INFO] Baue EDK II mit: {full_cmd}")

    # Shell=True, da komplexe Kombi-Befehle
    run(full_cmd, shell=True)



def main():
    args = parse_args()

    home = Path.home()
    workspace = home / args.name
    print(f"[INFO] Projektverzeichnis: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)

    os.chdir(workspace)
    print(f"[INFO] Arbeitsverzeichnis gewechselt zu: {workspace}")

    edk2_dir = workspace / "edk2"

    clone_edk2(edk2_dir)
    write_target_txt(edk2_dir, args.arch)
    build_edk2(edk2_dir, args.build)
    build(edk2_dir)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Fehler beim Ausführen: {e}")
        sys.exit(1)
