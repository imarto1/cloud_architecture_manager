"""Tests for server container initialization."""

from __future__ import annotations

import sys

import server.docker_entrypoint as entrypoint


def test_start_seeds_a_missing_database(tmp_path, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(entrypoint, "DATABASE_PATH", tmp_path / "missing.sqlite")
    monkeypatch.setattr(
        entrypoint.subprocess,
        "run",
        lambda command, check: calls.append(("seed", command, check)),
    )
    monkeypatch.setattr(
        entrypoint.os,
        "execv",
        lambda executable, command: calls.append(("start", executable, command)),
    )

    entrypoint.start()

    assert calls == [
        ("seed", [sys.executable, "-m", "server.init_db"], True),
        ("start", sys.executable, [sys.executable, "server/main.py"]),
    ]


def test_start_preserves_an_existing_database(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "architectures.sqlite"
    database_path.touch()
    calls = []
    monkeypatch.setattr(entrypoint, "DATABASE_PATH", database_path)
    monkeypatch.setattr(
        entrypoint.subprocess,
        "run",
        lambda *_args, **_kwargs: calls.append("seed"),
    )
    monkeypatch.setattr(
        entrypoint.os,
        "execv",
        lambda executable, command: calls.append(("start", executable, command)),
    )

    entrypoint.start()

    assert calls == [
        ("start", sys.executable, [sys.executable, "server/main.py"]),
    ]
