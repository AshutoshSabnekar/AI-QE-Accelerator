# Test Impact Analysis (TIA) — Implementation & Validation Report

## 1. Overview

The Test Impact Analysis (TIA) utility was implemented in the AI-QE-Accelerator repository to identify changed Python functions, determine their dependencies, map impacted functions to pytest markers, and execute only the tests associated with the impacted functionality.

The objective is to reduce unnecessary test execution while maintaining confidence that tests relevant to a code change are executed.

## 2. Implementation

### Components

- `tools/tia/dependency_map.py`
  - Defines function dependencies.
  - Maps calculator functions to pytest markers.

- `tools/tia/tia_runner.py`
  - Detects changed source files.
  - Detects changed functions using Python AST analysis.
  - Determines impacted functions through dependency analysis.
  - Maps impacted functions to pytest markers.
  - Executes the selected pytest tests.
  - Parses pytest results and reports metrics and status.

### Workflow

1. Identify changed source files relative to the configured Git baseline.
2. Compare baseline and current source code to identify changed functions.
3. Expand the changed-function list using the dependency map.
4. Map impacted functions to pytest markers.
5. Construct a pytest marker expression and run selected tests.
6. Parse the pytest output.
7. Report test counts, selection metrics, execution time, and pass/fail status.

## 3. Dependency Analysis Experiment

The calculator contains a shared validation function, `validate_number`, used by `factorial` and `square_root`.

When the changes included `factorial`, `square_root`, and `validate_number`, the dependency analysis identified the impacted functions and selected these pytest markers:

- `factorial`
- `square_root`

The resulting marker expression was:

```text
factorial or square_root
```

## 4. Functional Validation

### Successful test selection

The TIA selected and executed 20 tests from the 47-test suite.

Result:

- 20 passed
- 0 failed
- 27 deselected
- Pytest exit code: 0
- TIA status: SUCCESS

### Intentional defect experiment

An intentional defect was introduced in the `add()` function to validate whether TIA would select the relevant addition tests and detect failures.

The experiment demonstrated that:

- The changed `add()` function was detected.
- Addition tests were selected.
- The intentionally broken behavior caused tests to fail.
- The TIA result reported failure and a non-zero exit code.

The defect was then reverted, and the clean test run passed.

## 5. Benchmark Methodology

A comparison was performed between the full pytest suite and the TIA-selected test suite.

Each execution type was run five times. Pytest's reported execution duration was recorded for each run.

### Full-suite benchmark

| Run | Tests | Duration |
|---|---:|---:|
| 1 | 47 passed | 0.26 sec |
| 2 | 47 passed | 0.20 sec |
| 3 | 47 passed | 0.31 sec |
| 4 | 47 passed | 0.28 sec |
| 5 | 47 passed | 0.20 sec |

Summary:

- Average duration: 0.25 sec
- Median duration: 0.26 sec
- Fastest: 0.20 sec
- Slowest: 0.31 sec

### TIA benchmark

| Run | Tests | Duration |
|---|---:|---:|
| 1 | 20 passed, 27 deselected | 0.08 sec |
| 2 | 20 passed, 27 deselected | 0.09 sec |
| 3 | 20 passed, 27 deselected | 0.11 sec |
| 4 | 20 passed, 27 deselected | 0.11 sec |
| 5 | 20 passed, 27 deselected | 0.08 sec |

Summary:

- Average duration: 0.094 sec
- Median duration: 0.09 sec
- Fastest: 0.08 sec
- Slowest: 0.11 sec
- Tests selected: 20
- Tests deselected: 27

## 6. Benchmark Comparison

| Metric | Full Suite | TIA |
|---|---:|---:|
| Total tests collected | 47 | 47 |
| Tests executed | 47 | 20 |
| Tests passed | 47 | 20 |
| Tests deselected | 0 | 27 |
| Median pytest duration | 0.26 sec | 0.09 sec |
| Average pytest duration | 0.25 sec | 0.094 sec |

### Test reduction

```text
(47 - 20) / 47 × 100 = 57.45%
```

TIA executed 57.45% fewer tests for the validated change.

### Median execution-time reduction

```text
(0.26 - 0.09) / 0.26 × 100 = 65.38%
```

### Average execution-time reduction

```text
(0.25 - 0.094) / 0.25 × 100 = 62.4%
```

## 7. Conclusion

The TIA prototype was successfully implemented and experimentally validated.

In the five-run benchmark conducted on the calculator test suite:

- Test selection reduced the number of executed tests from 47 to 20.
- Test reduction was 57.45%.
- Median pytest execution duration decreased from 0.26 seconds to 0.09 seconds.
- Median measured execution-time reduction was 65.38%.
- All selected tests passed in the clean benchmark runs.
- The intentional-defect experiment demonstrated that the TIA could select relevant tests and detect a failure.

These results demonstrate the functionality of the prototype. Because the test suite is small and execution times are very short, timing results may be influenced by system and pytest startup overhead. The measurements should not be interpreted as a guaranteed performance improvement for larger projects.

## 8. Current Limitations and Future Enhancements

Potential future enhancements include:

- More robust handling of added, deleted, renamed, and nested functions.
- Handling source-file additions and deletions.
- Improved behavior when changed functions have no mapped test markers.
- Handling changes outside function bodies, such as module-level constants and imports.
- More robust test-selection mapping and dependency configuration.
- Automated benchmark report generation.
- CI integration to run TIA during pull requests.
- Evaluation against a larger, more realistic application test suite.

---

**Project:** AI-QE-Accelerator  
**Feature:** Test Impact Analysis (TIA)  
**Validation:** Functional experiments and five-run benchmark  
