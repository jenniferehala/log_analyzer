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

python3 "${SCRIPT_DIR}/log_analyzer.py" "${LOG_DIR}"
