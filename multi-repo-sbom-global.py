import json
import os
import subprocess
import argparse
from pathlib import Path

# === Config ===
REPOS_FILE = "repos.json"
WORKSPACE_DIR = Path("workspace")
OUTPUT_DIR = Path("sboms/_global")
ERROR_LOG = Path("error_log_global.txt")

ORT_CLI = "ort"

def run_scancode(repo_path, result_dir):
    scancode_output = result_dir / "scancode_results.json"
    try:
        subprocess.run([
            "scancode", str(repo_path),
            "--copyright",
            "--email",
            "--info",
            "--json-pp", str(scancode_output),
            "--license",
            "--package",
            "--processes", "6",
            "--url"
        ], check=True)
        print(f"[✓] ScanCode global OK")
    except subprocess.CalledProcessError as e:
        print("[✗] ScanCode global échoué : voir error_log_global.txt")
        with ERROR_LOG.open("a") as f:
            f.write(f"[ScanCode Global] Error: {e}\n")

def run_global_ort_analysis():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    analyzed_file = OUTPUT_DIR / "analyzer-result.yml"

    try:
        subprocess.run([
            ORT_CLI, "analyze",
            "-i", str(WORKSPACE_DIR),
            "-o", str(OUTPUT_DIR)
        ], check=True)

        subprocess.run([
            ORT_CLI, "report",
            "-i", str(analyzed_file),
            "-o", str(OUTPUT_DIR),
            "-f", "EvaluatedModel"
        ], check=True)

        print("[✓] Analyse + Report global terminés")

    except subprocess.CalledProcessError as e:
        print("[✗] Échec ORT global : voir error_log_global.txt")
        with ERROR_LOG.open("a") as f:
            f.write(f"[ORT Global] Error: {e}\n")

def main():
    if ERROR_LOG.exists():
        ERROR_LOG.unlink()

    WORKSPACE_DIR.mkdir(exist_ok=True)
    with open(REPOS_FILE) as f:
        repos = json.load(f)

    total = len(repos)

    for idx, entry in enumerate(repos, start=1):
        name = entry["name"]
        url = entry["url"]
        dest = WORKSPACE_DIR / name
        print(f"[{idx}/{total}] Clonage de {name}...")

        try:
            subprocess.run(["git", "clone", "--depth=1", url, str(dest)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[✗] Échec clone {name} : voir error_log_global.txt")
            with ERROR_LOG.open("a") as f:
                f.write(f"[{name}] Clone error: {e}\n")

    print("\n[🔎] Lancement de l'analyse globale ORT...")
    run_global_ort_analysis()

    print("\n[🔍] Lancement du ScanCode global...")
    run_scancode(WORKSPACE_DIR, OUTPUT_DIR)

    print("\n[✅] Analyse globale complète ! Résultats dans sboms/_global")

if __name__ == "__main__":
    main()
