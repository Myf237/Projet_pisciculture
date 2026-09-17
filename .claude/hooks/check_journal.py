"""Garde-fou SubagentStop — couche 3 de la règle de traçabilité.

Un sous-agent qui a modifié des fichiers ou exécuté des commandes doit avoir
écrit son entrée dans logs/agents/journal/ avant de rendre la main.
Sinon, il est renvoyé UNE seule fois compléter son journal (code de sortie 2).
Le renvoi est lui-même tracé dans logs/agents/actions.jsonl.

Toute erreur interne laisse le sous-agent terminer (code 0).
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "logs" / "agents" / "actions.jsonl"
STATE_DIR = ROOT / "logs" / "agents" / ".state"
JOURNAL_MARK = "logs/agents/journal/"
ACTING_TOOLS = {"Write", "Edit", "NotebookEdit", "Bash", "PowerShell"}
TOOL_EVENTS = {"PostToolUse", "PostToolUseFailure"}

REMINDER = (
    "Traçabilité : tu as modifié des fichiers ou exécuté des commandes sans écrire "
    "d'entrée dans logs/agents/journal/AAAA-MM-JJ.md. Ajoute maintenant ton entrée "
    "(format et règles : .claude/rules/tracabilite.md — Action, Fichiers, Pourquoi, "
    "Résultat avec preuve, Suite), puis rends la main.\n"
)


def agent_activity(agent_id: str) -> tuple[bool, bool]:
    """Retourne (a_agi, a_journalise) pour ce sous-agent d'après actions.jsonl."""
    acted = journaled = False
    if not LOG_FILE.exists():
        return acted, journaled
    with LOG_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("agent_id") != agent_id or record.get("event") not in TOOL_EVENTS:
                continue
            if record.get("tool") not in ACTING_TOOLS:
                continue
            target = str(record.get("target", "")).replace("\\", "/")
            if JOURNAL_MARK in target:
                journaled = journaled or record.get("status") == "ok"
            else:
                acted = True
    return acted, journaled


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        agent_id = payload.get("agent_id")
        if not agent_id:
            return 0
        marker = STATE_DIR / f"relance-{re.sub(r'[^A-Za-z0-9_-]', '_', agent_id)}"
        if marker.exists():  # déjà renvoyé une fois : ne jamais boucler
            return 0
        acted, journaled = agent_activity(agent_id)
        if not acted or journaled:
            return 0
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        marker.touch()
        record = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "event": "GardeFouJournal",
            "agent": payload.get("agent_type") or "sous-agent-interne",
            "agent_id": agent_id,
            "session": payload.get("session_id"),
            "decision": "renvoye_completer_journal",
        }
        with LOG_FILE.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        sys.stderr.buffer.write(REMINDER.encode("utf-8"))
        return 2
    except Exception:  # un garde-fou défaillant ne doit pas bloquer le projet
        return 0


if __name__ == "__main__":
    sys.exit(main())
