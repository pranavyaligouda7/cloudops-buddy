# src/tools/executor.py (improved)
import subprocess
import shlex
import logging
from typing import Dict, Any
from src.config.settings import settings

logger = logging.getLogger(__name__)

class CommandExecutor:
    DANGEROUS_PATTERNS = ["rm -rf", "delete", "terminate", "drop", "shutdown", "dd"]

    @staticmethod
    def is_safe(command: str) -> bool:
        # Split into arguments safely
        try:
            args = shlex.split(command)
        except ValueError:
            return False
        if not args:
            return False
        first_word = args[0]
        # Check if the base command is allowed
        if first_word not in settings.allowed_commands:
            logger.warning(f"Command '{first_word}' not in allowed list")
            return False
        # Also check the whole command for dangerous patterns (defense in depth)
        cmd_lower = command.lower()
        for pattern in CommandExecutor.DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                logger.warning(f"Dangerous pattern '{pattern}' detected")
                return False
        return True

    @staticmethod
    def execute(command: str, dry_run: bool = None) -> Dict[str, Any]:
        if dry_run is None:
            dry_run = settings.dry_run

        # First, validate safety (this also ensures command is parseable)
        if not CommandExecutor.is_safe(command):
            return {
                "status": "blocked",
                "output": f"⛔ Command blocked due to security policy: {command}"
            }

        if dry_run:
            return {
                "status": "dry_run",
                "output": f"🔍 [DRY RUN] Would execute: {command}\n"
                           "Set CLOUDOPS_BUDDY_DRY_RUN=false or use --execute to run."
            }

        # Split into arguments for safe execution
        try:
            args = shlex.split(command)
        except ValueError as e:
            return {"status": "error", "output": f"Invalid command syntax: {e}"}

        timeout = getattr(settings, "command_timeout", 30)  # make it configurable

        try:
            result = subprocess.run(
                args,  # list of arguments – no shell
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "output": output or "(no output)",
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": f"⏰ Command timed out after {timeout}s"}
        except FileNotFoundError:
            return {"status": "error", "output": f"Command not found: {args[0]}"}
        except Exception as e:
            return {"status": "error", "output": f"Execution error: {str(e)}"}