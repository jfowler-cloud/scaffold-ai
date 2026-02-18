#!/usr/bin/env python3
"""Manual test script for security gate workflow."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scaffold_ai.graph.workflow import create_workflow
from scaffold_ai.graph.state import GraphState


async def test_insecure_architecture():
    """Test that security gate blocks insecure architecture."""
    print("\n" + "=" * 60)
    print("TEST 1: Insecure Architecture (should FAIL)")
    print("=" * 60)

    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {
                    "id": "lambda-1",
                    "type": "lambda",
                    "data": {"label": "API Handler", "config": {}},
                },
                {
                    "id": "dynamodb-1",
                    "type": "dynamodb",
                    "data": {"label": "Users Table", "config": {}},
                },
            ],
            "edges": [{"source": "lambda-1", "target": "dynamodb-1"}],
        },
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    print(f"\n✓ Security Review Ran: {'security_review' in result}")
    if "security_review" in result:
        review = result["security_review"]
        print(f"✓ Security Score: {review.get('security_score', 0)}/100")
        print(f"✓ Passed: {review.get('passed', False)}")
        print(f"✓ Critical Issues: {len(review.get('critical_issues', []))}")
        print(f"✓ Code Generated: {len(result.get('generated_files', []))} files")

        if (
            not review.get("passed", False)
            and len(result.get("generated_files", [])) == 0
        ):
            print("\n✅ TEST PASSED: Security gate blocked insecure architecture")
            return True
        else:
            print("\n❌ TEST FAILED: Security gate did not block insecure architecture")
            return False
    else:
        print("\n❌ TEST FAILED: Security review did not run")
        return False


async def test_secure_architecture():
    """Test that security gate allows secure architecture."""
    print("\n" + "=" * 60)
    print("TEST 2: Secure Architecture (should PASS)")
    print("=" * 60)

    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {
                    "id": "cognito-1",
                    "type": "cognito",
                    "data": {"label": "Auth", "config": {"mfa": True}},
                },
                {
                    "id": "apigateway-1",
                    "type": "apigateway",
                    "data": {"label": "API", "config": {"auth": "cognito"}},
                },
                {
                    "id": "lambda-1",
                    "type": "lambda",
                    "data": {
                        "label": "Handler",
                        "config": {"environment_encryption": True},
                    },
                },
                {
                    "id": "dynamodb-1",
                    "type": "dynamodb",
                    "data": {
                        "label": "Data",
                        "config": {"encryption": True, "backup": True},
                    },
                },
            ],
            "edges": [
                {"source": "cognito-1", "target": "apigateway-1"},
                {"source": "apigateway-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "dynamodb-1"},
            ],
        },
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    print(f"\n✓ Security Review Ran: {'security_review' in result}")
    if "security_review" in result:
        review = result["security_review"]
        print(f"✓ Security Score: {review.get('security_score', 0)}/100")
        print(f"✓ Passed: {review.get('passed', False)}")
        print(f"✓ Critical Issues: {len(review.get('critical_issues', []))}")
        print(f"✓ Code Generated: {len(result.get('generated_files', []))} files")

        if review.get("passed", False) and len(result.get("generated_files", [])) > 0:
            print("\n✅ TEST PASSED: Security gate allowed secure architecture")
            return True
        else:
            print("\n❌ TEST FAILED: Security gate blocked secure architecture")
            return False
    else:
        print("\n❌ TEST FAILED: Security review did not run")
        return False


async def test_empty_architecture():
    """Test security gate with empty architecture."""
    print("\n" + "=" * 60)
    print("TEST 3: Empty Architecture (should PASS)")
    print("=" * 60)

    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {"nodes": [], "edges": []},
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    print(f"\n✓ Security Review Ran: {'security_review' in result}")
    if "security_review" in result:
        review = result["security_review"]
        print(f"✓ Security Score: {review.get('security_score', 0)}/100")
        print(f"✓ Passed: {review.get('passed', False)}")

        if review.get("passed", False) and review.get("security_score") == 100:
            print("\n✅ TEST PASSED: Empty architecture passed security review")
            return True
        else:
            print("\n❌ TEST FAILED: Empty architecture did not pass")
            return False
    else:
        print("\n❌ TEST FAILED: Security review did not run")
        return False


async def main():
    """Run all tests."""
    print("\n🔒 SECURITY GATE WORKFLOW TESTS")
    print("=" * 60)

    results = []

    try:
        results.append(await test_insecure_architecture())
    except Exception as e:
        print(f"\n❌ TEST 1 EXCEPTION: {e}")
        results.append(False)

    try:
        results.append(await test_secure_architecture())
    except Exception as e:
        print(f"\n❌ TEST 2 EXCEPTION: {e}")
        results.append(False)

    try:
        results.append(await test_empty_architecture())
    except Exception as e:
        print(f"\n❌ TEST 3 EXCEPTION: {e}")
        results.append(False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
