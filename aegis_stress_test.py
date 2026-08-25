import json
import time
from copy import deepcopy

import aegis_v8 as aegis


# ============================================================
# AEGIS OMEGA AFRICA V8
# Multi-Crisis Deterministic Stress Test
# Compatible with aegis_v8.py 8.2-competition-final
# ============================================================

TEST_SCENARIOS = [
    {"name": "Severe Flood", "data": {"crisis": "flood", "population": 1200, "injured": 35, "missing": 8, "clean_water_liters": 200, "generator_hours": 6, "nurses": 2, "volunteers": 12, "satellite_phones": 1, "electricity": 0, "internet": 0}},
    {"name": "Drought", "data": {"crisis": "drought", "population": 3500, "injured": 10, "missing": 0, "clean_water_liters": 500, "generator_hours": 4, "nurses": 3, "volunteers": 20, "satellite_phones": 1, "electricity": 0, "internet": 0}},
    {"name": "Cyclone", "data": {"crisis": "cyclone", "population": 2200, "injured": 80, "missing": 25, "clean_water_liters": 350, "generator_hours": 8, "nurses": 4, "volunteers": 30, "satellite_phones": 2, "electricity": 0, "internet": 0}},
    {"name": "Wildfire", "data": {"crisis": "wildfire", "population": 1800, "injured": 55, "missing": 6, "clean_water_liters": 300, "generator_hours": 5, "nurses": 3, "volunteers": 25, "satellite_phones": 1, "electricity": 1, "internet": 0}},
    {"name": "Landslide", "data": {"crisis": "landslide", "population": 900, "injured": 45, "missing": 20, "clean_water_liters": 160, "generator_hours": 4, "nurses": 2, "volunteers": 18, "satellite_phones": 1, "electricity": 0, "internet": 0}},
    {"name": "Clinic Power Failure", "data": {"crisis": "clinic_outage", "population": 700, "injured": 28, "missing": 0, "clean_water_liters": 120, "generator_hours": 3, "nurses": 4, "volunteers": 10, "satellite_phones": 1, "electricity": 0, "internet": 1}},
    {"name": "Telecom Blackout", "data": {"crisis": "telecom_outage", "population": 4000, "injured": 5, "missing": 3, "clean_water_liters": 600, "generator_hours": 7, "nurses": 5, "volunteers": 24, "satellite_phones": 2, "electricity": 1, "internet": 0}},
    {"name": "Water Contamination", "data": {"crisis": "water_contamination", "population": 2600, "injured": 20, "missing": 0, "clean_water_liters": 180, "generator_hours": 5, "nurses": 3, "volunteers": 18, "satellite_phones": 1, "electricity": 1, "internet": 0}},
    {"name": "Remote Village Isolation", "data": {"crisis": "infrastructure_failure", "population": 1500, "injured": 18, "missing": 4, "clean_water_liters": 250, "generator_hours": 5, "nurses": 2, "volunteers": 15, "satellite_phones": 1, "electricity": 0, "internet": 0}},
    {"name": "Mass Casualty Event", "data": {"crisis": "mass_casualty", "population": 5000, "injured": 250, "missing": 30, "clean_water_liters": 700, "generator_hours": 12, "nurses": 8, "volunteers": 50, "satellite_phones": 3, "electricity": 0, "internet": 0}},
]


def build_scenario(changes):
    scenario = deepcopy(aegis.DEFAULT_SCENARIO)
    scenario.update(changes)
    return scenario


def validate_plan_invariants(plan, scenario):
    errors = []

    required_sections = [
        "priorities", "allocation", "risks",
        "dependencies", "facts", "unknowns",
    ]
    for section in required_sections:
        if section not in plan:
            errors.append(f"Missing plan section: {section}")

    if len(plan.get("priorities", [])) != 5:
        errors.append("Plan must contain exactly 5 priorities")
    if len(plan.get("risks", [])) != 3:
        errors.append("Plan must contain exactly 3 risks")
    if len(plan.get("dependencies", [])) != 3:
        errors.append("Plan must contain exactly 3 dependencies")

    allocation = plan.get("allocation", {})
    expected_allocation = {
        "clean_water_liters_available": scenario["clean_water_liters"],
        "generator_hours_available": scenario["generator_hours"],
        "nurses_available": scenario["nurses"],
        "volunteers_available": scenario["volunteers"],
        "satellite_phones_available": scenario["satellite_phones"],
    }
    if allocation != expected_allocation:
        errors.append("Allocation does not exactly preserve available resources")

    facts = plan.get("facts", {})
    for key in aegis.DEFAULT_SCENARIO:
        if facts.get(key) != scenario.get(key):
            errors.append(f"Fact mismatch: {key}")

    return errors


def run_test(test):
    scenario = build_scenario(test["data"])
    start = time.perf_counter()

    input_errors = aegis.validate_input(scenario)
    if input_errors:
        return {
            "name": test["name"], "status": "FAIL", "severity": "-",
            "severity_score": 0, "confidence": 0,
            "time": time.perf_counter() - start,
            "errors": input_errors, "plan": None,
        }

    score = aegis.severity_score(scenario)
    level = aegis.severity_label(score)
    plan = aegis.build_safe_plan(scenario)
    errors = validate_plan_invariants(plan, scenario)
    confidence = aegis.calculate_rule_confidence(scenario)
    elapsed = time.perf_counter() - start

    return {
        "name": test["name"],
        "status": "PASS" if not errors else "FAIL",
        "severity": level,
        "severity_score": score,
        "confidence": confidence,
        "time": elapsed,
        "errors": errors,
        "plan": plan,
    }


def invalid_input_tests():
    cases = [
        ("injured > population", {"population": 100, "injured": 150}),
        ("missing > population", {"population": 100, "missing": 101}),
        ("injured + missing > population", {"population": 100, "injured": 60, "missing": 50}),
        ("negative resource", {"clean_water_liters": -1}),
        ("invalid electricity flag", {"electricity": 2}),
        ("invalid internet flag", {"internet": -1}),
        ("empty crisis", {"crisis": ""}),
        ("boolean numeric field", {"population": True}),
    ]

    results = []
    for name, changes in cases:
        scenario = build_scenario(changes)
        errors = aegis.validate_input(scenario)
        results.append({
            "name": name,
            "status": "PASS" if errors else "FAIL",
            "errors_detected": errors,
        })
    return results


def main():
    print()
    print("=" * 96)
    print("AEGIS OMEGA AFRICA V8 - MULTI-CRISIS STRESS TEST")
    print(f"ENGINE VERSION: {aegis.VERSION}")
    print("=" * 96)

    overall_start = time.perf_counter()
    results = []

    for test in TEST_SCENARIOS:
        result = run_test(test)
        results.append(result)
        print(
            f"{result['name']:<28}"
            f"{result['status']:<7}"
            f"{result['severity']:<10}"
            f"score={result['severity_score']:>3}  "
            f"confidence={result['confidence']:>3}  "
            f"time={result['time'] * 1000:>8.3f} ms"
        )
        if result["errors"]:
            for error in result["errors"]:
                print(f"  ERROR: {error}")

    invalid_results = invalid_input_tests()
    print("-" * 96)
    for result in invalid_results:
        print(f"Invalid: {result['name']:<34}{result['status']}")

    overall_elapsed = time.perf_counter() - overall_start
    passed = sum(r["status"] == "PASS" for r in results)
    invalid_passed = sum(r["status"] == "PASS" for r in invalid_results)
    final_ok = passed == len(results) and invalid_passed == len(invalid_results)
    final_status = "STRESS TEST PASSED" if final_ok else "STRESS TEST FAILED"

    print("=" * 96)
    print(f"VALID CRISIS TESTS : {passed}/{len(results)} PASSED")
    print(f"INVALID INPUT TESTS: {invalid_passed}/{len(invalid_results)} PASSED")
    print(f"FAILED TESTS       : {(len(results)-passed) + (len(invalid_results)-invalid_passed)}")
    print(f"TOTAL TEST TIME    : {overall_elapsed:.6f} sec")
    print(f"FINAL STATUS       : {final_status}")
    print("=" * 96)

    report = {
        "system": "AEGIS OMEGA AFRICA",
        "version": aegis.VERSION,
        "valid_tests_passed": passed,
        "valid_tests_total": len(results),
        "invalid_tests_passed": invalid_passed,
        "invalid_tests_total": len(invalid_results),
        "total_test_seconds": overall_elapsed,
        "final_status": final_status,
        "tests": results,
        "invalid_tests": invalid_results,
    }

    with open("aegis_stress_results.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("Detailed report saved to: aegis_stress_results.json")


if __name__ == "__main__":
    main()
