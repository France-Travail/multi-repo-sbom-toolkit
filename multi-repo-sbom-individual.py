import json
import os
import subprocess
import tempfile
import argparse
import yaml
import csv
from pathlib import Path

# === Configuration ===
REPOS_FILE = "repos.json"
OUTPUT_DIR = Path("sboms")
ERROR_LOG = Path("error_log.txt")
SUMMARY_FILE = OUTPUT_DIR / "summary.csv"

ORT_CLI = "ort"  

def count_dependencies(analyzer_result_path):
    try:
        with open(analyzer_result_path, 'r') as f:
            data = yaml.safe_load(f)
            dependencies = set()
            for proj in data.get("projects", []):
                for scope in proj.get("scopes", []):
                    for dep in scope.get("dependencies", []):
                        dependencies.add(dep.get("id", ""))
            return len(dependencies)
    except Exception:
        return 0

def run_ort_commands(repo_name, repo_path, skip_existing):
    result_dir = OUTPUT_DIR / repo_name
    result_dir.mkdir(parents=True, exist_ok=True)

    analyzed_file = result_dir / "analyzer-result.yml"
    evaluated_file = result_dir / "evaluatedModel.json"
    scancode_file = result_dir / "scancode_results.json"

    if skip_existing and analyzed_file.exists() and evaluated_file.exists() and scancode_file.exists():
        print(f"[↪] Analyse déjà présente pour {repo_name}, on saute (flag --skip-existing)")
        return

    try:
        subprocess.run([
            ORT_CLI, "analyze",
            "-i", str(repo_path),
            "-o", str(result_dir)
        ], check=True)

        subprocess.run([
            ORT_CLI, "report",
            "-i", str(analyzed_file),
            "-o", str(result_dir),
            "-f", "EvaluatedModel"
        ], check=True)

        run_scancode(repo_path, result_dir, repo_name)

        count = count_dependencies(analyzed_file)
        with SUMMARY_FILE.open("a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([repo_name, count])

        print(f"[✓] SBOM + ScanCode générés pour {repo_name} ({count} dépendances)")

    except subprocess.CalledProcessError as e:
        print(f"[✗] Échec ORT pour {repo_name} : voir error_log.txt")
        with ERROR_LOG.open("a") as f:
            f.write(f"[{repo_name}] ORT error: {e}\n")

def run_scancode(repo_path, result_dir, repo_name):
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
        print(f"[✓] ScanCode généré pour {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Échec ScanCode pour {repo_name} : voir error_log.txt")
        with ERROR_LOG.open("a") as f:
            f.write(f"[{repo_name}] ScanCode error: {e}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-existing", action="store_true", help="Ignorer les projets déjà analysés")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    if ERROR_LOG.exists():
        ERROR_LOG.unlink()

    if not SUMMARY_FILE.exists():
        with SUMMARY_FILE.open("w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["project", "dependency_count"])

    with open(REPOS_FILE) as f:
        repos = json.load(f)

    total = len(repos)

    for idx, entry in enumerate(repos, start=1):
        name = entry["name"]
        url = entry["url"]
        print(f"\n[{idx}/{total}] Traitement de {name}...")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                subprocess.run(["git", "clone", "--depth=1", url, tmpdir], check=True)
                run_ort_commands(name, tmpdir, args.skip_existing)
            except subprocess.CalledProcessError as e:
                print(f"[✗] Échec du clonage pour {name} : voir error_log.txt")
                with ERROR_LOG.open("a") as f:
                    f.write(f"[{name}] Clone error: {e}\n")

if __name__ == "__main__":
    main()