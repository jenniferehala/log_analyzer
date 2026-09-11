# log_analyzer — Airflow Log Analyzer Mini-Project

A small Python tool that walks an Airflow log directory, finds every
ERROR-level log entry (including multi-line tracebacks), and reports the
total count plus each error's full detail. Builds on
[airflow_mini_project](../airflow_mini_project) (the `marketvol` DAG) —
run against that project's real logs, this actually surfaces the real
yfinance failure that DAG hit on its first run.

## What it does

- `analyze_file(file)` parses one `.log` file and returns
  `(error_count, list_of_error_details)`.
- `log_analyzer.py` recursively finds every `*.log` file under a directory
  (`pathlib.Path(log_dir).rglob('*.log')`), calls `analyze_file` on each,
  and prints the cumulative count and every error's detail.

## Project layout

```
log_analyzer_mini_project/
├── log_analyzer.py      # analyze_file() + main() / CLI entry point
├── run_analyzer.sh       # shell wrapper
└── docs/
    └── execution_log.txt # real output from a run against project 1's logs
```

## Run it

Requires only Python 3.9+ (uses `pathlib`, no third-party dependencies).

```bash
# against any Airflow log directory:
python3 log_analyzer.py /path/to/airflow/logs

# or, using the shell wrapper, defaults to ../airflow_mini_project/logs:
./run_analyzer.sh
./run_analyzer.sh /path/to/airflow/logs   # explicit path also works
```

Output format:

```
Total number of errors: N
Here are all the errors:
[timestamp] {file.py:line} ERROR - message
...
```

## Verify the result

Run it against `airflow_mini_project/logs` (checked out as a sibling
folder) and you should see **19 errors** — these are genuinely real: the
`marketvol` DAG's `download_aapl`/`download_tsla` tasks failed twice before
a yfinance version fix (see that project's README), and every one of those
failures — including the full Python tracebacks — is a real ERROR entry in
those logs. `docs/execution_log.txt` has the full captured output.

You can also generate a synthetic example matching the assignment PDF's
sample log format to sanity-check the parser in isolation:

```bash
printf '%s\n' \
  "[2020-10-03 20:00:25,474] {scheduler_job.py:963} INFO - 2 tasks up for execution" \
  "[2020-09-26 20:15:33,479] {taskinstance.py:1150} ERROR - No columns to parse from file" \
  > /tmp/sample.log
python3 log_analyzer.py /tmp
# -> Total number of errors: 1
```

## A note on the brief's "t1/t2 operators" line

The assignment PDF's section 2.2 ends with: *"The Python operators should
call the analyze_file function. Name the operators t1 and t2 for the
symbols AAPL and TSLA, respectively."* This appears to be a leftover
line copy-pasted from the first mini-project's brief (which really does
define `t1`/`t2` PythonOperators for AAPL/TSLA downloads) — it doesn't fit
this project, which analyzes the whole log tree in one pass and is invoked
as a standalone CLI script (`python3 log_analyzer.py <dir>`), matching the
PDF's own usage example and sample output. Documenting that assumption
here rather than bolting on two Airflow operators that don't match the
rest of the spec.

## Submission checklist

- [x] Python code (`log_analyzer.py`) + shell script (`run_analyzer.sh`)
      pushed to GitHub
- [x] README with run/verify steps
- [x] `docs/execution_log.txt` — real command-line output from a
      successful run
