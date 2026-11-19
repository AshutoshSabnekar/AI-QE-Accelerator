from tools.tia.dependency_map import DEPENDENCIES
from tools.tia.dependency_map import FUNCTION_TEST_MARKERS

import ast
import re
from pathlib import Path
import subprocess
import sys


def get_changed_source_files(base_branch="main"):
    """
    Detect changed source files relative to a base branch.

    Includes:
    - Modified tracked files
    - Staged files
    - Untracked files

    Only files under src/ are returned.
    """

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    tracked_changes = subprocess.run(
        ["git", "diff", base_branch, "--name-only"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_root,
    ).stdout.splitlines()

    untracked_files = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_root,
    ).stdout.splitlines()

    changed_files = set(tracked_changes + untracked_files)

    source_files = [
        file.replace("\\", "/")
        for file in changed_files
        if file.replace("\\", "/").startswith("src/")
    ]

    return sorted(source_files)


def get_changed_functions(base_branch="main"):
    """
    Identify changed Python functions in changed source files.

    Compares the baseline version from Git with the current
    working version using Python AST.
    """

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )

    changed_files = get_changed_source_files(base_branch)

    changed_functions = {}

    for file_path in changed_files:

        if not file_path.endswith(".py"):
            continue

        baseline_result = subprocess.run(
            ["git", "show", f"{base_branch}:{file_path}"],
            capture_output=True,
            text=True,
            check=False,
            cwd=repo_root,
        )

        if baseline_result.returncode != 0:
            baseline_code = ""
        else:
            baseline_code = baseline_result.stdout

        current_file = repo_root / file_path
        current_code = current_file.read_text(encoding="utf-8")

        baseline_tree = ast.parse(baseline_code)
        current_tree = ast.parse(current_code)

        baseline_functions = extract_functions(baseline_tree)
        current_functions = extract_functions(current_tree)

        all_function_names = (
            set(baseline_functions) | set(current_functions)
        )

        modified_functions = []

        for function_name in all_function_names:

            baseline_function = baseline_functions.get(function_name)
            current_function = current_functions.get(function_name)

            if baseline_function != current_function:
                modified_functions.append(function_name)

        if modified_functions:
            changed_functions[file_path] = sorted(modified_functions)

    return changed_functions


def get_impacted_functions(changed_functions):
    """
    Return all functions impacted by changed functions.

    Includes direct and indirect dependencies.
    """

    impacted = set()
    pending = list(changed_functions)

    while pending:

        current = pending.pop()

        if current in impacted:
            continue

        impacted.add(current)

        dependents = DEPENDENCIES.get(current, [])
        pending.extend(dependents)

    return impacted


def get_impacted_markers(changed_functions):
    """
    Return pytest markers for all impacted functions.
    """

    impacted_functions = get_impacted_functions(changed_functions)

    markers = set()

    for function in impacted_functions:

        function_markers = FUNCTION_TEST_MARKERS.get(function, [])
        markers.update(function_markers)

    return markers


def run_impacted_tests(changed_functions):
    """
    Execute pytest tests associated with impacted functions
    and capture the execution results.
    """

    markers = get_impacted_markers(changed_functions)

    if not markers:

        print("No matching test markers found.")

        return {
            "return_code": 1,
            "stdout": "",
            "stderr": "No matching test markers found.",
            "markers": [],
        }

    marker_expression = " or ".join(sorted(markers))

    print(f"Impacted pytest markers: {marker_expression}")
    print("Running impacted tests...\n")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-m",
            marker_expression,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "markers": sorted(markers),
    }


def parse_pytest_results(output):
    """
    Parse pytest summary output into structured metrics.
    """

    metrics = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "deselected": 0,
        "xfailed": 0,
        "xpassed": 0,
        "duration_seconds": 0.0,
    }

    summary_lines = [
        line.strip()
        for line in output.splitlines()
        if " in " in line
        and any(
            status in line
            for status in [
                "passed",
                "failed",
                "skipped",
                "deselected",
                "xfailed",
                "xpassed",
            ]
        )
    ]

    if not summary_lines:
        return metrics

    summary = summary_lines[-1]

    status_pattern = re.compile(
        r"(\d+)\s+(passed|failed|skipped|deselected|xfailed|xpassed)"
    )

    for count, status in status_pattern.findall(summary):
        metrics[status] = int(count)

    duration_match = re.search(r"in\s+([\d.]+)s", summary)

    if duration_match:
        metrics["duration_seconds"] = float(
            duration_match.group(1)
        )

    return metrics


def extract_functions(tree):
    """
    Extract function definitions from an AST.

    Returns:
        Dictionary containing function names and AST representations.
    """

    functions = {}

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            function_name = node.name

            # Normalize AST so formatting and line numbers
            # don't affect the comparison.
            function_structure = ast.dump(
                node,
                include_attributes=False,
            )

            functions[function_name] = function_structure

    return functions


def run_tia(base_branch="main"):
    """
    Execute the complete Test Impact Analysis workflow.
    """

    print("\n========== TEST IMPACT ANALYSIS ==========\n")

    changed_files = get_changed_source_files(base_branch)

    if not changed_files:

        print("No changed source files detected.")

        return {
            "changed_files": [],
            "changed_functions": {},
            "impacted_functions": [],
            "selected_markers": [],
            "total_tests": 0,
            "selected_tests": 0,
            "selection_rate_percent": 0.0,
            "test_reduction_percent": 0.0,
            "test_metrics": {},
            "pytest_return_code": 0,
            "success": True,
        }

    print("Changed source files:")

    for file in changed_files:
        print(f"  - {file}")

    changed_functions = get_changed_functions(base_branch)

    print("\nChanged functions:")

    for file, functions in changed_functions.items():

        print(f"  {file}:")

        for function in functions:
            print(f"    - {function}")

    all_changed_functions = [
        function
        for functions in changed_functions.values()
        for function in functions
    ]

    impacted_functions = get_impacted_functions(
        all_changed_functions
    )

    print("\nImpacted functions:")

    for function in sorted(impacted_functions):
        print(f"  - {function}")

    markers = get_impacted_markers(impacted_functions)

    print("\nSelected pytest markers:")

    for marker in sorted(markers):
        print(f"  - {marker}")

    test_result = run_impacted_tests(impacted_functions)

    metrics = parse_pytest_results(test_result["stdout"])

    selected_tests = (
        metrics["passed"]
        + metrics["failed"]
        + metrics["skipped"]
        + metrics["xfailed"]
        + metrics["xpassed"]
    )

    total_tests = selected_tests + metrics["deselected"]

    selection_rate = (
        selected_tests / total_tests * 100
        if total_tests > 0
        else 0
    )

    reduction_rate = (
        metrics["deselected"] / total_tests * 100
        if total_tests > 0
        else 0
    )

    print("\n========== TIA EXECUTION REPORT ==========")

    print(f"Total tests       : {total_tests}")
    print(f"Tests selected    : {selected_tests}")
    print(f"Tests passed      : {metrics['passed']}")
    print(f"Tests failed      : {metrics['failed']}")
    print(f"Tests skipped     : {metrics['skipped']}")
    print(f"Tests deselected  : {metrics['deselected']}")

    print(f"Selection rate    : {selection_rate:.2f}%")
    print(f"Test reduction    : {reduction_rate:.2f}%")

    print(
        f"Execution time    : "
        f"{metrics['duration_seconds']} seconds"
    )

    print(f"Pytest exit code  : {test_result['return_code']}")

    if test_result["return_code"] == 0:
        print("\nTIA RESULT: SUCCESS")
    else:
        print("\nTIA RESULT: FAILURE")

    print("\n=========================================")

    return {
        "changed_files": changed_files,
        "changed_functions": changed_functions,
        "impacted_functions": sorted(impacted_functions),
        "selected_markers": sorted(markers),
        "total_tests": total_tests,
        "selected_tests": selected_tests,
        "selection_rate_percent": round(selection_rate, 2),
        "test_reduction_percent": round(reduction_rate, 2),
        "test_metrics": metrics,
        "pytest_return_code": test_result["return_code"],
        "success": test_result["return_code"] == 0,
    }