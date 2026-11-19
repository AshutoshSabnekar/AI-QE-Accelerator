# TIA Agent POC

## 1. Purpose

The TIA Agent is a rule-based proof of concept that uses the repository's existing Test Impact Analysis implementation to identify and execute tests related to source changes. It does not use an LLM, OpenAI, IBM Cloud, API keys, or external AI services.

## 2. Problem

Running the complete test suite for every code change can add unnecessary CI time and noise. The agent narrows execution to tests mapped to changed functions and the functions that depend on them.

## 3. Architecture

The POC has three main components:

- `tia_agent.py` invokes the TIA runner and evaluates its structured result.
- `tools/tia/tia_runner.py` detects changed source files and functions, identifies impacted functions, executes pytest markers, and calculates metrics.
- `tools/tia/dependency_map.py` contains the manual function dependency and function-to-pytest-marker mappings.

The GitHub Actions workflow in `.github/workflows/tia-agent.yml` executes the agent for feature-branch pushes and pull requests targeting `main`.

## 4. Execution Flow

```text
Developer pushes code
→ GitHub Actions triggers
→ TIA Agent starts
→ Changed code is analyzed
→ Impacted tests are identified
→ Selected tests execute
→ Agent evaluates results
→ CI reports PASS or FAIL
```

## 5. Changed Code Detection

The agent calls `run_tia(base_branch="main")`.

The runner determines changed source files by comparing `git diff main --name-only` with untracked files. It includes only paths under `src/`. It then compares each changed source file with its `main` version using Python AST structures to identify modified function definitions.

## 6. Impacted Test Selection

The runner expands changed functions through `DEPENDENCIES`, which maps functions to functions that depend on them.

It then uses `FUNCTION_TEST_MARKERS` to map impacted functions to pytest markers. The markers are combined into one pytest expression, for example:

```text
factorial or square_root
```

No complete-suite fallback is selected inside this POC. If no relevant marker can be determined, the agent fails safely and requests that the dependency/test mapping be reviewed.

## 7. Test Execution

The runner executes:

```text
python -m pytest -v -m "<marker expression>"
```

The captured pytest result includes the return code, standard output, standard error, and selected markers. The runner parses the pytest summary into passed, failed, skipped, deselected, xfailed, xpassed, and duration metrics.

## 8. Agent Evaluation

The runner returns structured fields including:

- `changed_files`
- `changed_functions`
- `impacted_functions`
- `selected_markers`
- `total_tests`
- `selected_tests`
- `selection_rate_percent`
- `test_reduction_percent`
- `test_metrics`
- `pytest_return_code`
- `success`

The agent reports these fields and makes a rule-based decision:

The agent also parses individual lines from pytest's verbose output and reports each test node ID with its `PASSED`, `FAILED`, `SKIPPED`, `XPASS`, or `XFAIL` status. The runner still executes only the marker-selected tests; it does not run the complete suite to create the report.

- No changed source files: no test execution required; exit `0`.
- Relevant markers and pytest return code `0`: targeted regression passed; exit `0`.
- Relevant markers and non-zero pytest return code: targeted regression failed; exit `1`.
- No relevant markers or an exception: critical TIA error; exit `1`.

## 9. GitHub Actions Integration

`.github/workflows/tia-agent.yml` triggers for:

- Pushes to branches other than `main`
- Pull requests targeting `main`

It does not trigger for direct pushes to `main`. The workflow checks out with `fetch-depth: 0`, creates or refreshes a local `main` baseline, sets up Python 3.14, installs `requirements.txt`, and runs `python tia_agent.py`.

There are no API secrets or external service credentials.

## 10. GitHub Job Summary

When `GITHUB_STEP_SUMMARY` is available in GitHub Actions, `tia_agent.py` appends a readable Markdown report containing:

- Changed file and changed function counts
- Total tests selected
- Passed, failed, and skipped test counts
- Pytest execution duration
- Test reduction percentage
- Agent PASS/FAIL status
- Changed source files and functions
- Individual executed test node IDs and statuses
- A separate list of failed test node IDs

The summary is written only from the targeted pytest execution already performed by the TIA runner. It does not execute the complete suite.

## 11. CI PASS and FAIL Rules

The workflow passes when `tia_agent.py` exits `0`:

- No source changes were detected, or
- Selected impacted tests passed.

The workflow fails when `tia_agent.py` exits `1`:

- Selected impacted tests failed, or
- No impacted test markers could be determined, or
- TIA could not complete due to a critical error.

## 12. Run Locally

From the project root:

```bash
python tia_agent.py
```

Or activate the project environment and run the equivalent command used on Windows:

```bash
.venv\Scripts\python.exe tia_agent.py
```

## 13. Successful Execution Example

```text
========== TIA AGENT ==========
[AGENT] Analyzing code changes...

========== TEST IMPACT ANALYSIS ==========
...
========== AGENT DECISION ==========
[AGENT] Targeted regression passed.
[AGENT] Recommendation: Targeted regression testing is recommended based on the dependency analysis.

========== TIA AGENT COMPLETED ==========
```

## 14. Failed Execution Example

```text
========== AGENT DECISION ==========
[AGENT] Targeted regression failed.
[AGENT] Recommendation: Investigate test failures before approving the code change.

========== TIA AGENT COMPLETED ==========
```

The process then exits non-zero, allowing GitHub Actions to mark the workflow as failed.

## 15. Current Limitations

- The dependency and test-marker mappings are manual.
- AST comparison is limited to function definitions.
- Module-level constants, imports, decorators, and changes outside function bodies may not be detected.
- Added, deleted, renamed, and nested functions have limited or no handling.
- Unknown changed functions have no affected tests unless they are mapped.
- Metrics describe the implementation's collected pytest result and are not a guarantee of full-regression coverage.
