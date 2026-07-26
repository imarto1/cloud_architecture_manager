"""Tests for server container initialization."""

from __future__ import annotations

import sys
from unittest.mock import Mock

import server.docker_entrypoint as entrypoint


def test_start_seeds_a_missing_database(tmp_path, monkeypatch) -> None:
    run = Mock()
    execv = Mock()
    monkeypatch.setattr(entrypoint, "DATABASE_PATH", tmp_path / "missing.sqlite")
    monkeypatch.setattr(entrypoint.subprocess, "run", run)
    monkeypatch.setattr(entrypoint.os, "execv", execv)

    entrypoint.start()

    run.assert_called_once_with(
        [sys.executable, "-m", "server.init_db"],
        check=True,
    )
    execv.assert_called_once_with(
        sys.executable,
        [sys.executable, "-m", "server.main"],
    )


def test_start_preserves_an_existing_database(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "architectures.sqlite"
    database_path.touch()
    run = Mock()
    execv = Mock()
    monkeypatch.setattr(entrypoint, "DATABASE_PATH", database_path)
    monkeypatch.setattr(entrypoint.subprocess, "run", run)
    monkeypatch.setattr(entrypoint.os, "execv", execv)

    entrypoint.start()

    run.assert_not_called()
    execv.assert_called_once_with(
        sys.executable,
        [sys.executable, "-m", "server.main"],
    )
