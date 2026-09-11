#!/usr/bin/env bash
# Wrapper for log_analyzer.py, per the submission's "shell script" requirement.
#
# Usage: run_analyzer.sh [log_dir]
#   log_dir defaults to ../airflow_mini_project/logs (the marketvol DAG's
#   Airflow log directory from the first mini-project, if it's checked out
#   as a sibling folder).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${1:-${SCRIPT_DIR}/../airflow_mini_project/logs}"

if [[ ! -d "${LOG_DIR}" ]]; then
    echo "ERROR: log directory not found: ${LOG_DIR}" >&2
    echo "Usage: $0 [log_dir]" >&2
    exit 1
fi

# Pick whichever Python actually runs. On Windows, `python3` on PATH is
# often a Microsoft Store alias stub that prints an install nag and exits
# nonzero rather than running anything - `command -v` still finds it, so
# we have to actually invoke --version to know it works.
PYTHON_BIN=""
for candidate in python3 python py; do
    if command -v "${candidate}" >/dev/null 2>&1 && "${candidate}" --version >/dev/null 2>&1; then
        PYTHON_BIN="${candidate}"
        break
    fi
done

if [[ -z "${PYTHON_BIN}" ]]; then
    echo "ERROR: no working Python interpreter found (tried python3, python, py)" >&2
    exit 1
fi

"${PYTHON_BIN}" "${SCRIPT_DIR}/log_analyzer.py" "${LOG_DIR}"
