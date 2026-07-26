"""Tests for the packaged Docker Compose lifecycle."""

from __future__ import annotations

from unittest.mock import Mock

from aws_parser_mocks import compose


def test_compose_project_applies_name_environment_and_parallelism(
    monkeypatch,
) -> None:
    run = Mock()
    monkeypatch.setattr(compose.subprocess, "run", run)

    compose.MockComposeProject(
        "test-project",
        {"WEB_APPLICATION_PORT": "5000"},
    ).up(parallelism=4)

    command = run.call_args.args[0]
    options = run.call_args.kwargs
    assert command[:2] == ["docker", "compose"]
    assert command[-5:] == ["--parallel", "4", "up", "--detach", "--wait"]
    assert "--project-name" in command
    assert "test-project" in command
    assert options["check"] is True
    assert options["env"]["WEB_APPLICATION_PORT"] == "5000"
