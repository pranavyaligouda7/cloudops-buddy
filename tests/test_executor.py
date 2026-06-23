import pytest
from src.tools.executor import CommandExecutor
from src.config.settings import settings

def test_is_safe_allowed():
    assert CommandExecutor.is_safe("aws s3 ls") is True

def test_is_safe_blocked_pattern():
    assert CommandExecutor.is_safe("rm -rf /") is False

def test_is_safe_unknown_command():
    assert CommandExecutor.is_safe("unknowncmd") is False

def test_execute_dry_run():
    settings.dry_run = True
    result = CommandExecutor.execute("aws s3 ls")
    assert result["status"] == "dry_run"