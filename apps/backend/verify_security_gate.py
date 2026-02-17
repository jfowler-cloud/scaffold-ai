#!/usr/bin/env python3
"""Verify security gate workflow structure without running it."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def verify_workflow_structure():
    """Verify the workflow has security gate properly integrated."""
    print("\n🔒 SECURITY GATE WORKFLOW VERIFICATION")
    print("=" * 60)

    # Read workflow file
    workflow_file = Path(__file__).parent / "src/scaffold_ai/graph/workflow.py"
    workflow_code = workflow_file.read_text()

    # Read nodes file
    nodes_file = Path(__file__).parent / "src/scaffold_ai/graph/nodes.py"
    nodes_code = nodes_file.read_text()

    checks = []

    # Check 1: Security review node exists
    print("\n✓ Checking security_review_node exists...")
    if "async def security_review_node" in nodes_code:
        print("  ✅ security_review_node function found")
        checks.append(True)
    else:
        print("  ❌ security_review_node function NOT found")
        checks.append(False)

    # Check 2: Security gate router exists
    print("\n✓ Checking security_gate router exists...")
    if "def security_gate(state: GraphState)" in nodes_code:
        print("  ✅ security_gate router function found")
        checks.append(True)
    else:
        print("  ❌ security_gate router function NOT found")
        checks.append(False)

    # Check 3: Security gate checks passed/failed
    print("\n✓ Checking security_gate logic...")
    if 'return "passed"' in nodes_code and 'return "failed"' in nodes_code:
        print("  ✅ security_gate returns passed/failed")
        checks.append(True)
    else:
        print("  ❌ security_gate does not return passed/failed")
        checks.append(False)

    # Check 4: Workflow adds security_review node
    print("\n✓ Checking workflow adds security_review node...")
    if 'workflow.add_node("security_review", security_review_node)' in workflow_code:
        print("  ✅ security_review node added to workflow")
        checks.append(True)
    else:
        print("  ❌ security_review node NOT added to workflow")
        checks.append(False)

    # Check 5: Workflow routes to security_review before code generation
    print("\n✓ Checking workflow routes to security_review...")
    if '"generate": "security_review"' in workflow_code:
        print("  ✅ Workflow routes to security_review on generate intent")
        checks.append(True)
    else:
        print("  ❌ Workflow does NOT route to security_review")
        checks.append(False)

    # Check 6: Security gate conditional routing
    print("\n✓ Checking security gate conditional routing...")
    if "security_gate," in workflow_code and '"passed": "cdk_specialist"' in workflow_code:
        print("  ✅ Security gate routes to cdk_specialist on pass")
        checks.append(True)
    else:
        print("  ❌ Security gate routing NOT configured")
        checks.append(False)

    # Check 7: Security gate blocks on failure
    print("\n✓ Checking security gate blocks on failure...")
    if '"failed": END' in workflow_code:
        print("  ✅ Security gate ends workflow on failure")
        checks.append(True)
    else:
        print("  ❌ Security gate does NOT block on failure")
        checks.append(False)

    # Check 8: Security review evaluates architecture
    print("\n✓ Checking security review evaluates architecture...")
    if "security_score" in nodes_code and "critical_issues" in nodes_code:
        print("  ✅ Security review calculates score and issues")
        checks.append(True)
    else:
        print("  ❌ Security review missing score/issues")
        checks.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Checks Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL CHECKS PASSED - Security gate is properly integrated")
        print("\nWorkflow Flow:")
        print("  1. interpret_intent")
        print("  2. architect_node")
        print("  3. [if intent=generate] → security_review_node")
        print("  4. [if security passed] → cdk_specialist_node")
        print("  5. [if security failed] → END (blocked)")
        return 0
    else:
        print(f"\n❌ {total - passed} CHECK(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = verify_workflow_structure()
    sys.exit(exit_code)
