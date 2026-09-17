"""Hook de journalisation automatique — couche 1 de la règle de traçabilité.

Appelé par Claude Code sur SessionStart, SubagentStart, SubagentStop,
PostToolUse, PostToolUseFailure et PermissionDenied (voir .claude/settings.json).
PermissionDenied ne couvre que les refus du mode auto : les refus dus aux règles
« deny » des settings ne déclenchent aucun hook et doivent être journalisés par l'agent.
Ajoute une ligne JSON par événement à logs/agents/actions.jsonl.

Ne bloque jamais le travail : une erreur interne est signalée sur stderr
et le script sort toujours avec le code 0.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "logs" / "agents" / "actions.jsonl"
MAIN_AGENT = "orchestrateur"
INTERNAL_SUBAGENT = "sous-agent-interne"  # sous-agent lancé par Claude Code lui-même (sans agent_type)
MAX_TARGET_LEN = 300
TOOL_STATUS = {"PostToolUse": "ok", "PostToolUseFailure": "echec", "PermissionDenied": "refuse"}

SESSION_REMINDER = (
    "[Projet Pisciculture IA] Traçabilité active : chaque action est journalisée "
    "automatiquement (logs/agents/actions.jsonl) et chaque agent DOIT écrire son entrée "
    "sémantique (logs/agents/journal/AAAA-MM-JJ.md, format .claude/rules/tracabilite.md). "
    "Commence par /demarrer-session et termine par /cloturer-session. "
    "État du projet : docs/11-TABLEAU_DE_BORD.md.\n"
)


def shorten(text: object, limit: int = MAX_TARGET_LEN) -> str:
    """Met le texte sur une ligne et le tronque à `limit` caractères."""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def relative_path(path_str: str) -> str:
    """Chemin relatif à la racine du projet (format POSIX) si possible."""
    try:
        return Path(path_str).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return str(path_str).replace("\\", "/")


def describe_target(tool: str, tool_input: dict) -> str:
    """Cible lisible d'un appel d'outil : fichier, commande, agent ou skill."""
    if tool in ("Write", "Edit"):
        return relative_path(tool_input.get("file_path", ""))
    if tool == "NotebookEdit":
        return relative_path(tool_input.get("notebook_path", ""))
    if tool in ("Bash", "PowerShell"):
        return shorten(tool_input.get("command", ""))
    if tool == "Agent":
        agent = tool_input.get("subagent_type") or "general-purpose"
        return shorten(f"{agent} : {tool_input.get('description', '')}")
    if tool == "Skill":
        return shorten(f"/{tool_input.get('skill', '')} {tool_input.get('args', '')}")
    return shorten(json.dumps(tool_input, ensure_ascii=False))


def build_record(payload: dict) -> dict:
    """Construit l'enregistrement JSON à partir de l'entrée du hook."""
    event = payload.get("hook_event_name", "")
    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": event,
        "agent": payload.get("agent_type") or (INTERNAL_SUBAGENT if payload.get("agent_id") else MAIN_AGENT),
        "agent_id": payload.get("agent_id"),
        "session": payload.get("session_id"),
    }
    if event in TOOL_STATUS:
        tool = payload.get("tool_name", "")
        tool_input = payload.get("tool_input") or {}
        record["tool"] = tool
        record["target"] = describe_target(tool, tool_input)
        if tool_input.get("description") and tool != "Agent":
            record["description"] = shorten(tool_input["description"], 150)
        record["status"] = TOOL_STATUS[event]
        if event == "PostToolUseFailure":
            error = payload.get("error")
            message = error.get("message", error) if isinstance(error, dict) else error
            record["error"] = shorten(message, 200)
    elif event == "SessionStart":
        record["source"] = payload.get("source")
    return {key: value for key, value in record.items() if value not in (None, "")}


def append_record(record: dict) -> None:
    """Ajoute l'enregistrement en fin de journal (append-only)."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw) if raw.strip() else {}
        if not payload.get("hook_event_name"):  # entrée vide ou inconnue : rien à tracer
            return 0
        if payload.get("hook_event_name") in ("SubagentStart", "SubagentStop") and not payload.get("agent_type"):
            return 0  # cycle de vie des sous-agents internes de Claude Code : aucune action sur le projet, bruit
        record = build_record(payload)
        append_record(record)
        if record.get("event") == "SessionStart":
            sys.stdout.buffer.write(SESSION_REMINDER.encode("utf-8"))
    except Exception as exc:  # la journalisation ne doit jamais bloquer le travail
        sys.stderr.buffer.write(f"[log_action] journalisation impossible : {exc}\n".encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
