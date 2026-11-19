import os

from tools.tia.tia_runner import run_tia


def markdown_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def print_test_cases(test_cases):
    print("[AGENT] Individual test results:")

    if not test_cases:
        print("  - No individual test case results were parsed.")
        return

    for test_case in test_cases:
        print(f"  - {test_case['status']}: {test_case['name']}")


def write_job_summary(result, changed_files, changed_functions, agent_result):
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    test_metrics = result.get("test_metrics", {})
    test_cases = result.get("test_cases", [])
    changed_function_count = sum(
        len(functions)
        for functions in changed_functions.values()
    )

    if agent_result.get("critical_error"):
        status = "FAIL"
    elif result.get("pytest_return_code", 1) == 0:
        status = "PASS"
    else:
        status = "FAIL"

    lines = [
        "# TIA Agent Report",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Changed files | {len(changed_files)} |",
        f"| Changed functions | {changed_function_count} |",
        f"| Tests selected | {result.get('selected_tests', 0)} |",
        f"| Tests passed | {test_metrics.get('passed', 0)} |",
        f"| Tests failed | {test_metrics.get('failed', 0)} |",
        f"| Tests skipped | {test_metrics.get('skipped', 0)} |",
        f"| Execution duration | {test_metrics.get('duration_seconds', 0):.2f}s |",
        f"| Test reduction | {result.get('test_reduction_percent', 0):.2f}% |",
        f"| Agent result | **{status}** |",
        "",
        "## Changed source files",
        "",
    ]

    if changed_files:
        lines.extend(f"- `{markdown_escape(file_name)}`" for file_name in changed_files)
    else:
        lines.append("- None")

    lines.extend(["", "## Changed functions", ""])
    if changed_functions:
        for file_name, functions in changed_functions.items():
            lines.append(f"### `{markdown_escape(file_name)}`")
            lines.extend(f"- `{markdown_escape(function_name)}`" for function_name in functions)
    else:
        lines.append("- None")

    lines.extend(["", "## Executed test cases", "", "| Test case | Status |", "|---|---|"])
    if test_cases:
        for test_case in test_cases:
            lines.append(
                f"| `{markdown_escape(test_case['name'])}` | {test_case['status']} |"
            )
    else:
        lines.append("| No individual test cases executed or parsed | - |")

    failed_cases = [
        test_case
        for test_case in test_cases
        if test_case["status"] == "FAILED"
    ]
    lines.extend(["", "## Failed test cases", ""])
    if failed_cases:
        lines.extend(
            f"- `{markdown_escape(test_case['name'])}`"
            for test_case in failed_cases
        )
    else:
        lines.append("- None")

    lines.extend(["", "## TIA recommendation", ""])
    if status == "PASS":
        lines.append("Targeted regression passed.")
    else:
        lines.append("Targeted regression failed or could not complete safely.")

    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")


def print_list(title, items):
    print(title)
    if not items:
        print("  - None")
        return

    for item in items:
        print(f"  - {item}")


def run_agent():
    print("\n========== TIA AGENT ==========")
    print("[AGENT] Analyzing code changes...")

    try:
        result = run_tia(base_branch="main")
    except Exception as error:
        print("\n========== AGENT DECISION ==========")
        print("[AGENT] Critical error: TIA could not complete.")
        print(f"[AGENT] Error: {error}")
        print("\n[AGENT] Recommendation: Investigate the TIA configuration or Git state.")
        print("\n========== TIA AGENT COMPLETED ==========")
        failed_result = {
            "success": False,
            "critical_error": True,
            "changed_files": [],
            "changed_functions": {},
            "impacted_functions": [],
            "selected_markers": [],
            "selected_tests": 0,
            "test_reduction_percent": 0,
            "test_metrics": {},
            "test_cases": [],
            "pytest_return_code": 1,
        }
        write_job_summary(failed_result, [], {}, {"critical_error": True})
        return failed_result

    changed_files = result.get("changed_files", [])

    print("\n========== AGENT DECISION ==========")

    print_list("[AGENT] Changed files:", changed_files)

    changed_functions = result.get("changed_functions", {})
    for file_name, functions in changed_functions.items():
        print(f"[AGENT] Changed functions in {file_name}:")
        for function_name in functions:
            print(f"  - {function_name}")

    print_list("[AGENT] Impacted functions:", result.get("impacted_functions", []))
    print_list("[AGENT] Selected test markers:", result.get("selected_markers", []))

    if not changed_files:
        print("\n[AGENT] No source changes detected.")
        print("[AGENT] No test execution required.")
        print("\n========== TIA AGENT COMPLETED ==========")
        write_job_summary(result, changed_files, changed_functions, {"critical_error": False})
        return result

    selected_markers = result.get("selected_markers", [])
    if not selected_markers:
        print("\n[AGENT] Critical error: No relevant test markers could be determined.")
        print("[AGENT] Recommendation: Add or update the dependency/test marker mapping.")
        print("\n========== TIA AGENT COMPLETED ==========")
        failed_result = {**result, "success": False, "critical_error": True}
        write_job_summary(failed_result, changed_files, changed_functions, {"critical_error": True})
        return failed_result

    print(f"\n[AGENT] Tests executed: {result.get('selected_tests', 0)}")
    print(f"[AGENT] Test selection rate: {result.get('selection_rate_percent', 0):.2f}%")
    print(f"[AGENT] Test reduction: {result.get('test_reduction_percent', 0):.2f}%")

    test_metrics = result.get("test_metrics", {})
    print(f"[AGENT] Tests passed: {test_metrics.get('passed', 0)}")
    print(f"[AGENT] Tests failed: {test_metrics.get('failed', 0)}")
    print(f"[AGENT] Tests skipped: {test_metrics.get('skipped', 0)}")
    print(f"[AGENT] Execution duration: {test_metrics.get('duration_seconds', 0):.2f}s")
    print_test_cases(result.get("test_cases", []))

    if result.get("pytest_return_code", 1) == 0:
        print("\n[AGENT] Targeted regression passed.")
        print(
            "[AGENT] Recommendation: Targeted regression testing "
            "is recommended based on the dependency analysis."
        )
    else:
        print("\n[AGENT] Targeted regression failed.")
        print(
            "[AGENT] Recommendation: Investigate test failures "
            "before approving the code change."
        )

    print("\n========== TIA AGENT COMPLETED ==========")
    write_job_summary(result, changed_files, changed_functions, {"critical_error": False})
    return result


if __name__ == "__main__":
    agent_result = run_agent()

    if agent_result.get("critical_error", False):
        raise SystemExit(1)

    if agent_result.get("pytest_return_code", 1) == 0:
        raise SystemExit(0)

    raise SystemExit(1)
