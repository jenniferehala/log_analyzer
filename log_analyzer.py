#!/usr/bin/env python3
"""
log_analyzer.py
----------------
Scans a directory tree of Airflow log files (*.log) and reports every
ERROR-level log entry found, plus the total error count.

Usage:
    python3 log_analyzer.py <log_dir> [--brief]

    --brief   print one line per error (the actual exception, not the
              full traceback) instead of the full multi-line detail.
              Optional convenience flag - default output (no flags) is
              what the assignment asks for.

Example:
    python3 log_analyzer.py ../airflow_mini_project/logs
    python3 log_analyzer.py ../airflow_mini_project/logs --brief
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Matches Airflow's standard log line header, e.g.:
#   [2026-09-11T21:29:39.351+0000] {multi.py:171} ERROR - message text
# Also matches the older Airflow 1.x timestamp style used in this project's
# brief:
#   [2020-10-03 20:00:25,474] {scheduler_job.py:963} INFO - message text
LOG_LINE_RE = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s*\{(?P<location>[^}]+)\}\s*"
    r"(?P<level>[A-Z]+)\s*-\s?(?P<message>.*)$"
)


@dataclass
class LogError:
    """One ERROR-level entry found in a log file."""

    timestamp: str
    location: str
    message: str

    def __str__(self) -> str:
        return f"[{self.timestamp}] {{{self.location}}} ERROR - {self.message}"

    def oneline(self) -> str:
        """A single-line summary: the last non-blank line of the message.

        For a plain one-line error this is just that line. For a Python
        traceback, the last line is the actual "ExceptionType: message"
        summary - the one line that matters - rather than the "Traceback
        (most recent call last):" header or the call-stack frames above it.
        """
        lines = [line.strip() for line in self.message.splitlines() if line.strip()]
        summary = lines[-1] if lines else "(no message)"
        return f"[{self.timestamp}] {{{self.location}}} ERROR - {summary}"


def analyze_file(file: Path) -> tuple[int, list[LogError]]:
    """Parse one .log file.

    Returns (error_count, list_of_error_details), e.g.:
        count, cur_list = analyze_file(file)

    Airflow log entries can span multiple physical lines (tracebacks,
    wrapped messages). Any line that isn't itself a new
    "[timestamp] {location} LEVEL - " header is treated as a continuation
    of whichever entry came immediately before it, and folded into that
    entry's message when that entry was an ERROR.
    """
    errors: list[LogError] = []
    current: LogError | None = None

    with file.open(encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            match = LOG_LINE_RE.match(line)

            if match:
                if match.group("level") == "ERROR":
                    current = LogError(
                        timestamp=match.group("timestamp"),
                        location=match.group("location"),
                        message=match.group("message"),
                    )
                    errors.append(current)
                else:
                    # a non-error header ends any error block in progress
                    current = None
            elif current is not None and line.strip():
                # continuation line (traceback, wrapped message, ...)
                current.message = f"{current.message}\n{line}".rstrip()

    return len(errors), errors


def main(argv: list[str]) -> int:
    args = argv[1:]
    brief = "--brief" in args
    positional = [a for a in args if a != "--brief"]

    if len(positional) != 1:
        print(f"usage: {argv[0]} <log_dir> [--brief]", file=sys.stderr)
        return 2

    log_dir = Path(positional[0])
    if not log_dir.is_dir():
        print(f"error: {log_dir} is not a directory", file=sys.stderr)
        return 2

    total_count = 0
    all_errors: list[LogError] = []

    for file in sorted(log_dir.rglob("*.log")):
        count, file_errors = analyze_file(file)
        total_count += count
        all_errors.extend(file_errors)

    print(f"Total number of errors: {total_count}")
    print("Here are all the errors:")
    for err in all_errors:
        print(err.oneline() if brief else err)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
