"""Garde-fou PreToolUse : limite les écritures d'un agent à son périmètre.

Déclaré dans le frontmatter d'un agent (hooks → PreToolUse, matcher Write|Edit|NotebookEdit) :
    python guard_paths.py <préfixe autorisé> [<préfixe autorisé> ...]

Un préfixe se terminant par « / » autorise tout le dossier ; sinon il désigne un fichier exact.
Écriture hors périmètre → refus (code 2) avec un message renvoyé à l'agent, et refus
tracé dans logs/agents/actions.jsonl (un refus au PreToolUse ne déclenche aucun autre hook).
Entrée illisible → refus également (le garde-fou échoue fermé).
"""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "logs" / "agents" / "actions.jsonl"


def relative_path(path_str: str) -> str:
    """Chemin relatif à la racine du projet (format POSIX), ou chemin brut si hors projet."""
    try:
        return Path(path_str).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return str(path_str).replace("\\", "/")


def is_allowed(rel_path: str, allowed: list[str]) -> bool:
    """Vrai si le chemin correspond à un fichier ou un dossier autorisé (casse ignorée, Windows)."""
    target = rel_path.casefold()
    for prefix in (p.replace("\\", "/").casefold() for p in allowed):
        if (prefix.endswith("/") and target.startswith(prefix)) or target == prefix:
            return True
    return False


def log_refusal(payload: dict, rel_path: str, allowed: list[str]) -> None:
    """Trace le refus dans le journal automatique, sans jamais empêcher le refus lui-même."""
    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": "PreToolUse",
        "agent": payload.get("agent_type") or ("sous-agent-interne" if payload.get("agent_id") else "orchestrateur"),
        "agent_id": payload.get("agent_id"),
        "session": payload.get("session_id"),
        "tool": payload.get("tool_name"),
        "target": rel_path,
        "status": "refuse",
        "error": f"hors périmètre (autorisé : {', '.join(allowed)})",
    }
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8", newline="\n") as handle:
            clean = {key: value for key, value in record.items() if value not in (None, "")}
            handle.write(json.dumps(clean, ensure_ascii=False) + "\n")
    except OSError:
        pass


def refuse(message: str) -> int:
    sys.stderr.buffer.write(message.encode("utf-8"))
    return 2


def main() -> int:
    allowed = sys.argv[1:]
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return refuse("Garde-fou de périmètre : entrée illisible, écriture refusée par précaution.\n")
    tool_input = payload.get("tool_input") or {}
    rel_path = relative_path(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if is_allowed(rel_path, allowed):
        return 0
    log_refusal(payload, rel_path, allowed)
    agent = payload.get("agent_type") or "cet agent"
    return refuse(
        f"Écriture refusée : « {rel_path} » est hors du périmètre de {agent} "
        f"(autorisé : {', '.join(allowed)}). Ne contourne pas ce refus : signale le besoin "
        "dans ton compte rendu pour que l'orchestrateur le délègue à l'agent propriétaire.\n"
    )


if __name__ == "__main__":
    sys.exit(main())
