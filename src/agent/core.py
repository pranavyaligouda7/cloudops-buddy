# src/agent/core.py
import json
import re
import logging
import click
from src.tools.executor import CommandExecutor

logger = logging.getLogger(__name__)

class CloudOpsAgent:
    def __init__(self, llm_client, execute_mode: bool = False):
        self.llm = llm_client
        self.execute_mode = execute_mode

        self.system_prompt = """
You are CloudOps Buddy, a DevOps assistant.

**Your response format (always valid JSON):**

1. For a single command:
{"action": "command", "command": "your command here", "explanation": "brief explanation"}

2. For a sequential procedure (installation, setup, etc.):
{
  "action": "steps",
  "steps": [
    {"command": "sudo apt update", "description": "Update package lists"},
    {"command": "sudo apt install default-jdk", "description": "Install Java"}
  ],
  "explanation": "Overall explanation"
}
**Important:** The `command` field MUST contain the exact CLI command to run. The `description` must be a short (≤5 words) explanation.

3. For a general list of related commands (examples, reference):
{"action": "list", "items": [{"command": "...", "description": "..."}], "explanation": "..."}
(same rule: `command` is the exact CLI command, `description` is a short label)

4. For explaining a concept (Kubernetes, AWS, etc.):
{"action": "explain", "explanation": "...", "key_features": ["...", "..."], "components": ["...", "..."]}

5. For error diagnosis:
{"action": "diagnose", "root_cause": "...", "fix": "..."}

6. If you need to execute a command to gather info:
{"action": "execute", "command": "...", "reason": "..."}

**Rules:**
- Use "steps" only when order matters (e.g., installation).
- Use "list" for unordered command examples.
- Use "explain" for conceptual questions.
- Keep commands safe – prefer read‑only.
- Always output valid JSON.
"""
        self.history = []

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        context = self._build_context(user_input)
        response = self.llm.send_message(context, self.system_prompt)
        self.history.append({"role": "assistant", "content": response})

        # Extract JSON
        json_str = response
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                json_str = match.group(0)

        try:
            decision = json.loads(json_str)
        except json.JSONDecodeError:
            return response

        action = decision.get("action")

        # --- Execute ---
        if action == "execute":
            cmd = decision.get("command")
            if self.execute_mode:
                if not click.confirm(f"Execute command:\n{cmd}\n\nProceed?"):
                    return f"⏹️ Cancelled.\n\n```bash\n{cmd}\n```"
                result = CommandExecutor.execute(cmd, dry_run=False)
            else:
                result = CommandExecutor.execute(cmd, dry_run=True)
            return f"Executed: {cmd}\n\nResult:\n{result['output']}"

        # --- Single command ---
        elif action == "command":
            cmd = decision.get("command")
            explanation = decision.get("explanation", "")
            if self.execute_mode:
                if not click.confirm(f"Execute command:\n{cmd}\n\nProceed?"):
                    return f"⏹️ Cancelled.\n\n```bash\n{cmd}\n```"
                result = CommandExecutor.execute(cmd, dry_run=False)
                output = result['output']
                if len(output) > 2000:
                    output = output[:2000] + "\n... (truncated)"
                return (
                    f"💡 {explanation}\n\n```bash\n{cmd}\n```\n\n"
                    f"**Result (exit code: {result.get('exit_code', 'N/A')}):**\n```\n{output}\n```"
                )
            else:
                return f"💡 {explanation}\n\n```bash\n{cmd}\n```"

        # --- Sequential steps (installation, setup) ---
        elif action == "steps":
            steps = decision.get("steps", [])
            explanation = decision.get("explanation", "")
            if not steps:
                return "No steps provided."

            formatted = f"💡 {explanation}\n\n"
            for i, step in enumerate(steps, 1):
                cmd = step.get("command", "")
                desc = step.get("description", "")
                formatted += f"**Step {i}:** {desc}\n```bash\n{cmd}\n```\n\n"

            if self.execute_mode:
                results = []
                for i, step in enumerate(steps, 1):
                    cmd = step.get("command", "")
                    desc = step.get("description", "")
                    if not click.confirm(f"Execute step {i}: {desc}\n{cmd}\n\nProceed?"):
                        return f"⏹️ Stopped at step {i} ({desc}).\n\n```bash\n{cmd}\n```"
                    result = CommandExecutor.execute(cmd, dry_run=False)
                    results.append(f"Step {i}: {desc}\n{result['output']}")
                    if result['status'] == "failed":
                        return f"❌ Step {i} failed: {desc}\n{result['output']}"
                return formatted + f"**✅ All steps executed successfully.**\n\n" + "\n".join(results)
            else:
                return formatted

        # --- Unordered list of commands (examples, reference) ---
        elif action == "list":
            items = decision.get("items", [])
            explanation = decision.get("explanation", "")
            if not items:
                return "No commands provided."

            formatted = f"💡 {explanation}\n\n"
            for item in items:
                cmd = item.get("command", "")
                desc = item.get("description", "")
                formatted += f"- **{desc}**: `{cmd}`\n"
            return formatted

        # --- Explanation of a concept ---
        elif action == "explain":
            explanation = decision.get("explanation", "")
            key_features = decision.get("key_features", [])
            components = decision.get("components", [])

            output = f"📖 **Explanation**\n\n{explanation}\n\n"
            if key_features:
                output += "**Key Features:**\n"
                for feat in key_features:
                    output += f"- {feat}\n"
                output += "\n"
            if components:
                output += "**Components:**\n"
                for comp in components:
                    output += f"- {comp}\n"
            return output

        # --- Error diagnosis ---
        elif action == "diagnose":
            return f"🔍 **Root Cause**: {decision.get('root_cause')}\n\n✅ **Fix**: {decision.get('fix')}"

        else:
            return response

    def _build_context(self, user_input: str) -> str:
        if not self.history:
            return user_input
        recent = self.history[-10:]
        lines = []
        for msg in recent:
            lines.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(lines)