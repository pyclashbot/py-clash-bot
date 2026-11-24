"""Supervisor CLI: deterministic plan/validate and a safe dry-run."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pyclashbot.supervisor.cli import main

if TYPE_CHECKING:
    from pathlib import Path


def _json(capsys: Any) -> Any:
    return json.loads(capsys.readouterr().out)


def test_plan_is_deterministic(capsys) -> None:
    assert main(["plan", "--count", "2"]) == 0
    payload = _json(capsys)
    assert [guest["serial"] for guest in payload["guests"]] == [
        "127.0.0.1:5570",
        "127.0.0.1:5571",
    ]
    assert [guest["server_port"] for guest in payload["guests"]] == [5560, 5561]


def test_validate_accepts_a_plan(capsys, tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    assert main(["plan", "--count", "2"]) == 0
    plan.write_text(capsys.readouterr().out, encoding="utf-8")

    assert main(["validate", str(plan)]) == 0
    payload = _json(capsys)
    assert payload["ok"] is True
    assert payload["count"] == 2


def test_validate_rejects_duplicate_serial(capsys, tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    guest = {
        "index": 0,
        "server_port": 5560,
        "device_port": 5570,
        "ip": "10.0.2.15",
        "mac": "02:00:00:00:00:01",
        "serial": "127.0.0.1:5570",
    }
    plan.write_text(json.dumps({"guests": [guest, guest]}), encoding="utf-8")

    assert main(["validate", str(plan)]) == 2
    payload = _json(capsys)
    assert payload["ok"] is False
    assert "index" in payload["error"]


def test_validate_rejects_malformed_json(capsys, tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text("{not json", encoding="utf-8")
    assert main(["validate", str(plan)]) == 2
    assert _json(capsys)["ok"] is False


def test_run_dry_run_prints_argv_env_without_spawning(capsys) -> None:
    assert main(["run", "--count", "1"]) == 0
    payload = _json(capsys)
    assert payload["dry_run"] is True
    guest = payload["guests"][0]
    assert guest["serial"] == "127.0.0.1:5570"
    assert guest["env"]["ADB_SERIAL"] == "127.0.0.1:5570"
    assert guest["env"]["ADB_MDNS"] == "0"
    assert guest["argv"][guest["argv"].index("--adb-serial") + 1] == guest["serial"]
