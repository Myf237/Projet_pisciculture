"""Garde-fou PreToolUse des commandes shell — règle systémique Git.

Référence : .claude/rules/git-workflow.md (§6).
- Sous-agents : seules les commandes git en lecture seule sont autorisées.
- Tous : refus des opérations irréversibles ou qui contournent le flux par pull request
  (force push, commit/merge/push sur main, --no-verify, amend d'un commit poussé,
  rebase, reset --hard, clean -f, branch -D, …).

Refus → code 2, message renvoyé à l'agent, ligne `refuse` dans logs/agents/actions.jsonl.
Toute erreur interne laisse passer la commande : ce garde-fou ne doit jamais bloquer le shell.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "logs" / "agents" / "actions.jsonl"
PROTECTED_BRANCH = "main"
MAIN_AGENT = "orchestrateur"

READ_ONLY = {
    "status", "diff", "log", "show", "ls-files", "ls-tree", "blame", "rev-parse", "describe",
    "shortlog", "grep", "check-ignore", "cat-file", "count-objects", "help", "version",
    "rev-list", "merge-base", "name-rev", "for-each-ref", "show-ref",
}
BRANCH_LISTING_OPTIONS = {
    "--show-current", "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "-l", "--list",
    "--contains", "--no-contains", "--merged", "--no-merged", "--points-at", "--sort", "--format",
    "--column", "--no-column", "--color", "--no-color", "--abbrev", "--no-abbrev", "-i", "--ignore-case",
}
TAG_LISTING_OPTIONS = {"-l", "--list", "-n", "--contains", "--no-contains", "--points-at", "--sort", "--format", "--merged", "--no-merged"}
CONFIG_READ_OPTIONS = {"--get", "--get-all", "--get-regexp", "--list", "-l"}
CONFIG_WRITE_OPTIONS = {"--add", "--unset", "--unset-all", "--replace-all", "--rename-section", "--remove-section", "-e", "--edit"}
GLOBAL_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
COMMAND_PREFIXES = {"&", "sudo", "command", "time", "exec"}
SEPARATORS = re.compile(r"&&|\|\||;|\||\r?\n")
SIMPLE_TOKEN = re.compile(r"[\w./:@+~^-]+")


def neutralize_quotes(command: str) -> str:
    """Retire heredocs, here-strings et textes cités (messages) pour éviter les faux positifs.

    Un texte cité sans espace (ex. "main") est conservé sans ses guillemets.
    """
    command = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2[ \t]*(?=\n|$)", " HEREDOC ", command, flags=re.S)
    command = re.sub(r"@'.*?'@|@\".*?\"@", " HERESTRING ", command, flags=re.S)

    def replace(match: re.Match) -> str:
        inner = match.group(0)[1:-1]
        return inner if SIMPLE_TOKEN.fullmatch(inner) else " TEXTE "

    return re.sub(r"'[^']*'|\"[^\"]*\"", replace, command)


def git_invocations(command: str) -> list[tuple[str, list[str]]]:
    """Liste des (sous-commande, arguments) pour chaque appel git du texte de commande."""
    invocations = []
    for segment in SEPARATORS.split(neutralize_quotes(command)):
        tokens = segment.split()
        while tokens and (tokens[0] in COMMAND_PREFIXES or re.fullmatch(r"\w+=\S*", tokens[0])):
            tokens.pop(0)
        if not tokens or Path(tokens[0]).name.lower() not in ("git", "git.exe"):
            continue
        index = 1
        while index < len(tokens) and tokens[index].startswith("-"):
            option = tokens[index]
            index += 2 if option in GLOBAL_OPTIONS_WITH_VALUE else 1
        if index < len(tokens):
            invocations.append((tokens[index], tokens[index + 1:]))
    return invocations


def run_git(*args: str) -> str:
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=10)
    return result.stdout.strip()


def current_branch() -> str:
    """Branche courante, y compris une branche sans commit ; chaîne vide si HEAD détachée."""
    return run_git("symbolic-ref", "--short", "-q", "HEAD")


def head_is_pushed() -> bool:
    return bool(run_git("branch", "-r", "--contains", "HEAD"))


def short_flags(args: list[str]) -> str:
    """Concatène les options courtes (-fdx → « fdx »)."""
    return "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))


def is_read_only(sub: str, args: list[str]) -> bool:
    """Vrai si la commande git ne modifie ni le dépôt, ni sa configuration, ni le distant."""
    if sub in READ_ONLY:
        return True
    names = {a.split("=")[0] for a in args if a.startswith("-")}
    positional = [a for a in args if not a.startswith("-")]
    if sub == "branch":
        selects = names & {"-l", "--list", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"}
        return names <= BRANCH_LISTING_OPTIONS and (not positional or bool(selects))
    if sub == "tag":
        return names <= TAG_LISTING_OPTIONS and (not positional or bool(names & {"-l", "--list"}))
    if sub == "remote":
        return names <= {"-v", "--verbose"} and positional[:1] in ([], ["show"], ["get-url"])
    if sub == "config":
        return bool(names & CONFIG_READ_OPTIONS) and not names & CONFIG_WRITE_OPTIONS
    if sub == "stash":
        return positional[:1] in (["list"], ["show"])
    if sub == "reflog":
        return positional[:1] in ([], ["show"])
    return False


def refusal_reason(sub: str, args: list[str], is_subagent: bool, branch_of) -> str | None:
    """Raison du refus, ou None si la commande est conforme à la règle git."""
    if is_subagent and not is_read_only(sub, args):
        return (f"« git {sub} » est réservé à l'orchestrateur — les sous-agents n'ont accès "
                "qu'aux commandes git en lecture seule ; signale le besoin dans ton compte rendu")
    flags = {a.split("=")[0] for a in args if a.startswith("-")}
    positional = [a for a in args if not a.startswith("-")]
    shorts = short_flags(args)
    on_main = lambda: branch_of() == PROTECTED_BRANCH  # noqa: E731 — évaluation paresseuse

    if "--no-verify" in flags or (sub == "commit" and "n" in shorts):
        return "--no-verify contourne les vérifications"
    if sub == "push":
        if flags & {"--force", "--force-with-lease", "--mirror", "--delete", "--prune", "--all"} or "f" in shorts or "d" in shorts:
            return "push destructif ou global (force, miroir, suppression, --all)"
        refspecs = positional[1:]
        if any(r.startswith(("+", ":")) for r in refspecs):
            return "refspec forcé ou de suppression"
        targets = [r.split(":")[-1] for r in refspecs]
        if any(t in (PROTECTED_BRANCH, f"refs/heads/{PROTECTED_BRANCH}") for t in targets):
            return "push direct sur main — passer par une pull request"
        if (not refspecs or "HEAD" in targets) and on_main():
            return "push direct sur main — passer par une pull request"
    elif sub == "commit":
        if on_main():
            return "commit direct sur main — créer une branche : git switch -c <type>/<sujet> origin/main"
        if "--amend" in flags and head_is_pushed():
            return "amend d'un commit déjà poussé (historique publié immuable) — faire un nouveau commit"
    elif sub == "merge":
        if on_main() and not flags & {"--abort", "--quit"}:
            return "merge local sur main — la fusion se fait par pull request après G2"
    elif sub == "pull":
        if on_main() and "--ff-only" not in flags:
            return "pull sur main sans --ff-only — utiliser git pull --ff-only"
    elif sub == "rebase":
        return "rebase (réécriture d'historique) — intégrer main par git merge origin/main"
    elif sub == "reset":
        if flags & {"--hard", "--merge", "--keep"}:
            return "reset destructif"
    elif sub == "clean":
        if "--force" in flags or "f" in shorts:
            return "clean -f supprime définitivement des fichiers non suivis"
    elif sub == "branch":
        if flags & {"--force"} or set(shorts) & set("DfMC"):
            return "suppression ou écrasement forcé de branche — utiliser git branch -d"
    elif sub == "switch":
        if flags & {"--force-create", "--discard-changes", "--force"} or set(shorts) & set("Cf"):
            return "switch forcé (écrase une branche ou des modifications)"
    elif sub == "checkout":
        if flags & {"--force"} or set(shorts) & set("Bf") or "--" in args or "." in positional:
            return "checkout destructif (écrase des modifications ou force une branche)"
    elif sub == "restore":
        staged = "--staged" in flags or "S" in shorts
        worktree = "--worktree" in flags or "W" in shorts
        if not staged or worktree:
            return "restore écrase les modifications du répertoire de travail (seul --staged est autorisé)"
    elif sub == "stash":
        if positional[:1] in (["drop"], ["clear"]):
            return "stash drop/clear supprime définitivement des modifications"
    elif sub in ("filter-branch", "filter-repo", "replace", "update-ref"):
        return "manipulation bas niveau de l'historique"
    elif sub == "tag":
        if flags & {"--delete", "--force"} or set(shorts) & set("df"):
            return "suppression ou écrasement de tag"
    elif sub == "reflog":
        if positional[:1] in (["expire"], ["delete"]):
            return "purge du reflog"
    elif sub == "gc":
        if any(a.startswith("--prune") for a in args):
            return "gc --prune supprime des objets récupérables"
    return None


def log_refusal(payload: dict, command: str, reason: str) -> None:
    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": "PreToolUse",
        "agent": payload.get("agent_type") or ("sous-agent-interne" if payload.get("agent_id") else MAIN_AGENT),
        "agent_id": payload.get("agent_id"),
        "session": payload.get("session_id"),
        "tool": payload.get("tool_name"),
        "target": " ".join(command.split())[:300],
        "status": "refuse",
        "error": f"règle git : {reason}"[:200],
    }
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8", newline="\n") as handle:
            clean = {key: value for key, value in record.items() if value not in (None, "")}
            handle.write(json.dumps(clean, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        command = str((payload.get("tool_input") or {}).get("command", ""))
        if "git" not in command:
            return 0
        is_subagent = bool(payload.get("agent_id"))
        cache: dict[str, str] = {}

        def branch_of() -> str:
            if "branch" not in cache:
                cache["branch"] = current_branch()
            return cache["branch"]

        for sub, args in git_invocations(command):
            reason = refusal_reason(sub, args, is_subagent, branch_of)
            if reason:
                log_refusal(payload, command, reason)
                sys.stderr.buffer.write(
                    (f"Commande git refusée : {reason}.\nRègle : .claude/rules/git-workflow.md. "
                     "Journalise ce refus (type ÉCHEC). S'il s'agit d'une action irréversible réellement "
                     "nécessaire, escalade à l'humain (G4) : il peut l'exécuter lui-même.\n").encode("utf-8"))
                return 2
    except Exception as exc:  # le garde-fou ne doit jamais bloquer le shell sur une erreur interne
        sys.stderr.buffer.write(f"[guard_git] vérification impossible : {exc}\n".encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
