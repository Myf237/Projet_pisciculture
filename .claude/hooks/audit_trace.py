"""Audit croisé des deux journaux de traçabilité.

Vérifie, pour une date donnée, que :
  1. chaque fichier du projet modifié (actions.jsonl) apparaît dans le journal sémantique ;
  2. chaque entrée sémantique respecte le format (Action, Fichiers, Pourquoi, Résultat, Suite).

Usage :
    python .claude/hooks/audit_trace.py                 # date du jour
    python .claude/hooks/audit_trace.py --date 2026-09-17

Code de sortie : 0 si conforme, 1 si écarts détectés.
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "logs" / "agents" / "actions.jsonl"
JOURNAL_DIR = ROOT / "logs" / "agents" / "journal"
FILE_TOOLS = {"Write", "Edit", "NotebookEdit"}
COMMAND_TOOLS = {"Bash", "PowerShell"}
REQUIRED_FIELDS = ("**Action :**", "**Fichiers :**", "**Pourquoi :**", "**Résultat :**", "**Suite :**")
ENTRY_HEADER = re.compile(r"^### (J-\d{8}-\d{3}) · (\d{2}:\d{2}) · ([\w-]+) · (\w+)", re.MULTILINE)


def load_actions(day: str) -> list[dict]:
    """Enregistrements automatiques dont l'horodatage correspond au jour."""
    if not LOG_FILE.exists():
        return []
    records = []
    with LOG_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(record.get("ts", "")).startswith(day):
                records.append(record)
    return records


def is_project_file(target: str) -> bool:
    """Vrai pour un chemin relatif du projet (exclut scratchpad, mémoire, etc.)."""
    return bool(target) and not re.match(r"^([A-Za-z]:|/)", target)


def audit(day: str) -> int:
    actions = load_actions(day)
    journal_path = JOURNAL_DIR / f"{day}.md"
    journal = journal_path.read_text(encoding="utf-8") if journal_path.exists() else ""

    modified = sorted({
        r["target"] for r in actions
        if r.get("tool") in FILE_TOOLS and r.get("status") == "ok"
        and is_project_file(r.get("target", ""))
        and not r["target"].startswith("logs/agents/journal/")
    })
    missing = [path for path in modified if path not in journal]

    headers = list(ENTRY_HEADER.finditer(journal))
    malformed = []
    for index, match in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(journal)
        block = journal[match.start():end]
        absent = [field for field in REQUIRED_FIELDS if field not in block]
        if absent:
            malformed.append(f"{match.group(1)} (manque : {', '.join(absent)})")

    actions_by_agent = Counter(r.get("agent", "?") for r in actions if r.get("tool") in FILE_TOOLS | COMMAND_TOOLS)
    entries_by_agent = Counter(match.group(3) for match in headers)
    failures = [r for r in actions if r.get("status") in ("echec", "refuse")]

    print(f"# Audit de traçabilité — {day}\n")
    print(f"- Journal sémantique : {journal_path.relative_to(ROOT).as_posix()} "
          f"({'présent' if journal else 'ABSENT'}, {len(headers)} entrée(s))")
    print(f"- Actions automatiques (fichiers + commandes) : {sum(actions_by_agent.values())}")
    print(f"- Échecs ou refus d'outils enregistrés : {len(failures)}")
    for record in failures:
        print(f"  - {str(record.get('ts', ''))[11:16]} · {record.get('agent')} · {record.get('tool')} · "
              f"{record.get('status')} · {record.get('target')} — {record.get('error', '')}")
    print()

    print("| Agent | Actions auto | Entrées journal |\n|---|---|---|")
    for agent in sorted(set(actions_by_agent) | set(entries_by_agent)):
        print(f"| {agent} | {actions_by_agent[agent]} | {entries_by_agent[agent]} |")

    print(f"\n## Fichiers modifiés non cités dans le journal ({len(missing)})")
    print("\n".join(f"- ❌ {path}" for path in missing) or "- ✅ aucun")
    print(f"\n## Entrées mal formées ({len(malformed)})")
    print("\n".join(f"- ❌ {entry}" for entry in malformed) or "- ✅ aucune")

    compliant = not missing and not malformed
    print(f"\n**Verdict : {'✅ CONFORME' if compliant else '❌ ÉCARTS À CORRIGER'}**")
    return 0 if compliant else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit croisé des journaux de traçabilité.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Jour audité (AAAA-MM-JJ)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    return audit(args.date)


if __name__ == "__main__":
    sys.exit(main())
