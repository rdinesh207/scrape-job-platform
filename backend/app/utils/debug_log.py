from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


DEBUG_LOG_PATH = Path(__file__).resolve().parents[3] / "debug-568b27.log"


def debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict[str, Any]) -> None:
    payload = {
        "sessionId": "568b27",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        # Debug logging must never break business logic.
        return
