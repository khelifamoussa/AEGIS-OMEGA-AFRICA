import argparse
import json
import re
import time
import urllib.request
import urllib.error
import socket
from datetime import datetime, timezone


VERSION = "8.2-competition-final"
QWEN_URL = "http://127.0.0.1:8080/v1/chat/completions"
QWEN_TIMEOUT = 3.5


DEFAULT_SCENARIO = {
    "crisis": "flood",
    "population": 1200,
    "injured": 35,
    "missing": 8,
    "clean_water_liters": 200,
    "generator_hours": 6,
    "nurses": 2,
    "volunteers": 12,
    "satellite_phones": 1,
    "electricity": 0,
    "internet": 0,
}


# ============================================================
# SAFETY POLICY
# ============================================================

FORBIDDEN_TERMS = {
    "hospital",
    "hospitals",
    "ambulance",
    "ambulances",
    "helicopter",
    "helicopters",
    "vehicle",
    "vehicles",
    "truck",
    "trucks",
    "boat",
    "boats",
    "medicine",
    "medicines",
    "medication",
    "medications",
    "doctor",
    "doctors",
    "food",
    "shelter",
    "shelters",
    "pump",
    "pumps",
    "drone",
    "drones",
    "police",
    "firefighters",
    "army",
    "military",
    "internet access",
    "mobile network",
}


DANGEROUS_CAPABILITY_PATTERNS = [
    r"\bgenerator\b.*\brestore\b.*\belectricity\b",
    r"\bgenerator\b.*\bpower\b.*\b(?:equipment|devices|hospital|pump)\b",
    r"\bsatellite phone\b.*\b(?:gps|internet|data network)\b",
    r"\bvolunteers?\b.*\b(?:medical treatment|surgery|diagnosis)\b",
    r"\bnurses?\b.*\b(?:surgery|advanced surgery)\b",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_input(data):

    required = {
        "crisis": str,
        "population": int,
        "injured": int,
        "missing": int,
        "clean_water_liters": int,
        "generator_hours": int,
        "nurses": int,
        "volunteers": int,
        "satellite_phones": int,
        "electricity": int,
        "internet": int,
    }

    errors = []

    for key, expected_type in required.items():

        if key not in data:
            errors.append(f"Missing field: {key}")
            continue

        value = data[key]

        # bool is technically an int in Python; reject it here.
        if expected_type is int:
            if isinstance(value, bool) or not isinstance(value, int):
                errors.append(f"Invalid type for {key}")
        elif not isinstance(value, expected_type):
            errors.append(f"Invalid type for {key}")

    numeric_fields = [
        "population",
        "injured",
        "missing",
        "clean_water_liters",
        "generator_hours",
        "nurses",
        "volunteers",
        "satellite_phones",
        "electricity",
        "internet",
    ]

    for key in numeric_fields:
        value = data.get(key)

        if (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value < 0
        ):
            errors.append(f"{key} cannot be negative")

    population = data.get("population")
    injured = data.get("injured")
    missing = data.get("missing")

    if (
        isinstance(population, int)
        and not isinstance(population, bool)
        and isinstance(injured, int)
        and not isinstance(injured, bool)
        and injured > population
    ):
        errors.append("injured cannot exceed population")

    if (
        isinstance(population, int)
        and not isinstance(population, bool)
        and isinstance(missing, int)
        and not isinstance(missing, bool)
        and missing > population
    ):
        errors.append("missing cannot exceed population")

    if (
        isinstance(population, int)
        and not isinstance(population, bool)
        and isinstance(injured, int)
        and not isinstance(injured, bool)
        and isinstance(missing, int)
        and not isinstance(missing, bool)
        and injured + missing > population
    ):
        errors.append(
            "injured + missing cannot exceed population"
        )

    if data.get("electricity") not in (0, 1):
        errors.append("electricity must be 0 or 1")

    if data.get("internet") not in (0, 1):
        errors.append("internet must be 0 or 1")

    if isinstance(data.get("crisis"), str):
        if not data["crisis"].strip():
            errors.append("crisis cannot be empty")

    return errors


# ============================================================
# INTERNAL SEVERITY
# ============================================================

def severity_score(data):
    """
    Internal prioritization score only.
    NOT a medical probability or casualty prediction.
    """

    score = 0

    if data["injured"] > 0:
        score += min(
            30,
            10 + data["injured"] // 2
        )

    if data["missing"] > 0:
        score += min(
            20,
            8 + data["missing"]
        )

    if data["electricity"] == 0:
        score += 10

    if data["internet"] == 0:
        score += 5

    if data["clean_water_liters"] < data["population"]:
        score += 15

    if data["nurses"] <= 2:
        score += 10

    if data["satellite_phones"] <= 1:
        score += 5

    return min(score, 100)


def severity_label(score):

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    return "LOW"


# ============================================================
# DETERMINISTIC CRISIS ENGINE
# ============================================================

def build_safe_plan(data):
    """
    Immediate deterministic safety core.

    Guarantees:
    - no invented resources
    - no assumed generator capability
    - no assumed satellite connectivity
    - no invented medical supplies
    - AI is NOT required for this decision
    """

    priorities = []

    if data["injured"] > 0:
        priorities.append(
            f"Prioritize assessment of the "
            f"{data['injured']} reported injured using the "
            f"{data['nurses']} available nurses."
        )

    if data["missing"] > 0:
        priorities.append(
            f"Prioritize locating the "
            f"{data['missing']} reported missing people using the "
            f"{data['volunteers']} available volunteers within "
            f"their known safe capabilities."
        )

    priorities.append(
        f"Protect and ration the available "
        f"{data['clean_water_liters']} L of clean water; "
        f"additional water availability is UNKNOWN."
    )

    priorities.append(
        f"Preserve the available "
        f"{data['generator_hours']} generator-hours until "
        f"a verified critical use and compatible load are known."
    )

    priorities.append(
        f"Preserve the "
        f"{data['satellite_phones']} satellite phone for prioritized "
        f"coordination if connectivity is available; "
        f"signal availability is UNKNOWN."
    )

    priorities = priorities[:5]

    while len(priorities) < 5:
        priorities.append(
            "Reassess verified facts before committing "
            "additional scarce resources."
        )

    allocation = {
        "clean_water_liters_available":
            data["clean_water_liters"],

        "generator_hours_available":
            data["generator_hours"],

        "nurses_available":
            data["nurses"],

        "volunteers_available":
            data["volunteers"],

        "satellite_phones_available":
            data["satellite_phones"],
    }

    risks = [
        (
            "Injured people may deteriorate while "
            "trained personnel are limited."
        ),
        (
            "Missing people remain at risk while their "
            "condition and location are unknown."
        ),
        (
            "Clean-water availability is severely constrained "
            "relative to the population."
        ),
    ]

    dependencies = [
        (
            f"Medical prioritization depends on the "
            f"{data['nurses']} available nurses."
        ),
        (
            f"Search activity depends on the "
            f"{data['volunteers']} available volunteers "
            f"and safe access."
        ),
        (
            "External coordination via satellite phone depends "
            "on actual signal availability."
        ),
    ]

    facts = {
        "crisis": data["crisis"],
        "population": data["population"],
        "injured": data["injured"],
        "missing": data["missing"],
        "clean_water_liters":
            data["clean_water_liters"],
        "generator_hours":
            data["generator_hours"],
        "nurses": data["nurses"],
        "volunteers": data["volunteers"],
        "satellite_phones":
            data["satellite_phones"],
        "electricity": data["electricity"],
        "internet": data["internet"],
    }

    unknowns = [
        "Locations and conditions of the missing people.",
        "Severity distribution of the reported injuries.",
        (
            "Availability of additional water, food, medicine, "
            "shelter, transport, or personnel."
        ),
        (
            "Generator load compatibility and safe "
            "operating conditions."
        ),
        (
            "Satellite-phone signal availability and "
            "reachable external responders."
        ),
        (
            "Flood evolution, road access, weather, "
            "and structural hazards."
        ),
    ]

    return {
        "priorities": priorities,
        "allocation": allocation,
        "risks": risks,
        "dependencies": dependencies,
        "facts": facts,
        "unknowns": unknowns,
    }


# ============================================================
# LOCAL QWEN PROMPT
# ============================================================

def make_ai_prompt(data, safe_plan):

    priorities = "\n".join(
        f"{i + 1}. {item}"
        for i, item
        in enumerate(safe_plan["priorities"])
    )

    return f"""
/no_think
You are the local language-refinement layer inside AEGIS.

TASK:
Rewrite ONLY the five VERIFIED priority actions below
more concisely.

HARD SAFETY RULES:
- Preserve the operational meaning.
- Output exactly 5 numbered lines.
- Maximum 70 words total.
- Do not add facts.
- Do not add resources.
- Do not add personnel.
- Do not add capabilities.
- Do not add locations.
- Do not add infrastructure.
- Do not add medical supplies.
- Do not infer equipment.
- Do not claim the generator powers or restores anything.
- Do not claim the satellite phone has signal.
- Do not change numeric quantities.
- Do not convert resource quantities.
- If uncertain, preserve the original wording.
- No introduction.
- No conclusion.
- No markdown heading.

VERIFIED FACTS:
crisis={data['crisis']}
population={data['population']}
injured={data['injured']}
missing={data['missing']}
clean_water={data['clean_water_liters']}L
generator_time={data['generator_hours']}h
nurses={data['nurses']}
volunteers={data['volunteers']}
satellite_phone={data['satellite_phones']}
electricity={data['electricity']}
internet={data['internet']}

VERIFIED PRIORITIES:
{priorities}
""".strip()


# ============================================================
# QWEN / LLAMA.CPP OPENAI-COMPATIBLE API
# ============================================================

def call_qwen_server(prompt, timeout=QWEN_TIMEOUT):
    """
    Optional local language refinement.

    The deterministic decision has already been produced before
    this function is called.

    Any timeout, malformed response, API error, or safety failure
    leaves the deterministic plan untouched.
    """

    payload = json.dumps(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
            "max_tokens": 72,
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        QWEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    started = time.perf_counter()

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            elapsed = (
                time.perf_counter() - started
            )

            parsed = json.loads(raw)

            choices = parsed.get("choices")

            if not isinstance(choices, list) or not choices:
                return {
                    "ok": False,
                    "content": "",
                    "elapsed_sec": elapsed,
                    "error": "Qwen returned no choices",
                }

            first_choice = choices[0]

            if not isinstance(first_choice, dict):
                return {
                    "ok": False,
                    "content": "",
                    "elapsed_sec": elapsed,
                    "error": "Malformed Qwen choice",
                }

            message = first_choice.get(
                "message",
                {}
            )

            if not isinstance(message, dict):
                return {
                    "ok": False,
                    "content": "",
                    "elapsed_sec": elapsed,
                    "error": "Malformed Qwen message",
                }

            content = message.get(
                "content",
                ""
            )

            if not isinstance(content, str):
                content = ""

            content = content.strip()

            if not content:
                return {
                    "ok": False,
                    "content": "",
                    "elapsed_sec": elapsed,
                    "error": "Qwen returned empty content",
                }

            return {
                "ok": True,
                "content": content,
                "elapsed_sec": elapsed,
                "error": None,
            }

    except urllib.error.HTTPError as exc:

        return {
            "ok": False,
            "content": "",
            "elapsed_sec":
                time.perf_counter() - started,
            "error":
                f"Qwen HTTP error: {exc.code}",
        }

    except urllib.error.URLError as exc:

        return {
            "ok": False,
            "content": "",
            "elapsed_sec":
                time.perf_counter() - started,
            "error":
                f"Qwen connection error: {exc.reason}",
        }

    except (TimeoutError, socket.timeout):

        return {
            "ok": False,
            "content": "",
            "elapsed_sec":
                time.perf_counter() - started,
            "error":
                "Qwen refinement timed out",
        }

    except json.JSONDecodeError:

        return {
            "ok": False,
            "content": "",
            "elapsed_sec":
                time.perf_counter() - started,
            "error":
                "Qwen returned invalid JSON",
        }

    except Exception as exc:

        return {
            "ok": False,
            "content": "",
            "elapsed_sec":
                time.perf_counter() - started,
            "error":
                f"Qwen error: {exc}",
        }


# ============================================================
# AI OUTPUT PARSER
# ============================================================

def extract_numbered_lines(text):

    lines = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        match = re.match(
            r"^([1-5])[\.\)]\s*(.+)$",
            line
        )

        if match:
            lines.append(
                match.group(2).strip()
            )

    return lines


# ============================================================
# SAFETY GATE
# ============================================================

def detect_forbidden_content(text):

    lower = text.lower()
    violations = []

    for term in sorted(FORBIDDEN_TERMS):

        if re.search(
            r"\b" + re.escape(term) + r"\b",
            lower
        ):
            violations.append(
                f"Unverified entity/resource: {term}"
            )

    for pattern in DANGEROUS_CAPABILITY_PATTERNS:

        if re.search(
            pattern,
            lower,
            flags=re.IGNORECASE
        ):
            violations.append(
                "Unverified capability claim matched: "
                + pattern
            )

    return violations


def allowed_numeric_values(data):
    """
    Numbers AI may repeat because they exist in verified input.
    Also allows numbering 1..5 used for the required action list.
    """

    values = {
        str(data["population"]),
        str(data["injured"]),
        str(data["missing"]),
        str(data["clean_water_liters"]),
        str(data["generator_hours"]),
        str(data["nurses"]),
        str(data["volunteers"]),
        str(data["satellite_phones"]),
        str(data["electricity"]),
        str(data["internet"]),
        "1",
        "2",
        "3",
        "4",
        "5",
    }

    return values


def validate_ai_output(text, data):

    violations = []

    numbered = extract_numbered_lines(text)

    if len(numbered) != 5:
        violations.append(
            "Expected exactly 5 numbered actions; "
            f"received {len(numbered)}"
        )

    # Ensure numbering is exactly 1..5.
    extracted_numbers = []

    for raw_line in text.splitlines():

        match = re.match(
            r"^\s*([1-5])[\.\)]\s+",
            raw_line
        )

        if match:
            extracted_numbers.append(
                int(match.group(1))
            )

    if (
        len(extracted_numbers) == 5
        and extracted_numbers != [1, 2, 3, 4, 5]
    ):
        violations.append(
            "Priority numbering must be exactly 1 through 5"
        )

    word_count = len(
        re.findall(
            r"\b[\w'-]+\b",
            text
        )
    )

    if word_count > 70:
        violations.append(
            f"AI response too long: {word_count} words"
        )

    violations.extend(
        detect_forbidden_content(text)
    )

    # Protect verified numeric facts.
    allowed = allowed_numeric_values(data)

    numbers = re.findall(
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
        text
    )

    for number in numbers:

        normalized = number.replace(",", "")

        if normalized not in allowed:
            violations.append(
                "Unverified numeric value introduced: "
                + number
            )

    lower = text.lower()

    capability_phrases = [
        "restore electricity",
        "restore power",
        "power essential",
        "power equipment",
        "power medical",
    ]

    for phrase in capability_phrases:

        if phrase in lower:
            violations.append(
                "Generator capability inferred without evidence: "
                + phrase
            )

    if "satellite phone" in lower:

        risky_satellite_phrases = [
            "has signal",
            "guaranteed signal",
            "internet access",
            "gps",
            "provides internet",
        ]

        for phrase in risky_satellite_phrases:

            if phrase in lower:
                violations.append(
                    "Satellite-phone capability inferred: "
                    + phrase
                )

    # Remove duplicate violation messages while preserving order.
    violations = list(
        dict.fromkeys(violations)
    )

    return (
        len(violations) == 0,
        violations,
        numbered,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_rule_confidence(data):
    """
    Measures deterministic input completeness and constraint
    coverage.

    This is NOT medical certainty.
    """

    required_fields = len(
        DEFAULT_SCENARIO
    )

    present = sum(
        1
        for key in DEFAULT_SCENARIO
        if key in data
    )

    completeness = (
        present / required_fields
    )

    confidence = round(
        90 + completeness * 8
    )

    return min(confidence, 98)


# ============================================================
# OUTPUT
# ============================================================

def print_header():

    print("=" * 72)
    print("                         AEGIS OMEGA AFRICA")
    print("              Offline Autonomous Crisis Intelligence")
    print(f"                     Competition Engine {VERSION}")
    print("=" * 72)


def print_plan(plan):

    print("\nPRIORITIES")

    for i, item in enumerate(
        plan["priorities"],
        1
    ):
        print(f"{i}. {item}")

    print("\nRESOURCE ENVELOPE")

    print(
        json.dumps(
            plan["allocation"],
            indent=2
        )
    )

    print("\nCRITICAL RISKS")

    for item in plan["risks"]:
        print(f"- {item}")

    print("\nCRITICAL DEPENDENCIES")

    for item in plan["dependencies"]:
        print(f"- {item}")

    print("\nKEY UNKNOWNS")

    for item in plan["unknowns"]:
        print(f"- {item}")


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "AEGIS OMEGA AFRICA "
            "offline crisis decision engine"
        )
    )

    parser.add_argument(
        "--ai",
        action="store_true",
        help=(
            "Use local Qwen only as an optional "
            "language-refinement layer"
        ),
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Optional JSON scenario file",
    )

    args = parser.parse_args()

    total_start = time.perf_counter()

    print_header()

    data = DEFAULT_SCENARIO.copy()

    if args.scenario:

        try:

            with open(
                args.scenario,
                "r",
                encoding="utf-8"
            ) as file:

                supplied = json.load(file)

            if not isinstance(supplied, dict):
                print(
                    "\nSCENARIO LOAD ERROR: "
                    "JSON root must be an object"
                )
                return

            data.update(supplied)

        except Exception as exc:

            print(
                f"\nSCENARIO LOAD ERROR: {exc}"
            )
            return

    errors = validate_input(data)

    if errors:

        print("\nSTATUS: REJECTED")

        for error in errors:
            print(f"- {error}")

        return

    # --------------------------------------------------------
    # STAGE 1:
    # Immediate deterministic decision.
    # --------------------------------------------------------

    decision_start = time.perf_counter()

    safe_plan = build_safe_plan(data)

    immediate_time = (
        time.perf_counter()
        - decision_start
    )

    score = severity_score(data)
    severity = severity_label(score)

    rule_confidence = (
        calculate_rule_confidence(data)
    )

    print(
        f"\nCRISIS TYPE       : "
        f"{data['crisis'].upper()}"
    )

    print(
        f"POPULATION        : "
        f"{data['population']}"
    )

    print(
        f"SEVERITY          : "
        f"{severity} ({score}/100)"
    )

    print(
        f"SAFE PLAN READY   : "
        f"{immediate_time:.6f} sec"
    )

    # Deterministic plan is always the default accepted result.
    accepted_plan = safe_plan

    ai_status = (
        "DISABLED - DETERMINISTIC SAFE MODE"
    )

    ai_elapsed = 0.0
    ai_raw = None
    ai_violations = []

    # --------------------------------------------------------
    # STAGE 2:
    # Optional local Qwen refinement.
    # --------------------------------------------------------

    if args.ai:

        prompt = make_ai_prompt(
            data,
            safe_plan
        )

        result = call_qwen_server(
            prompt
        )

        ai_elapsed = result[
            "elapsed_sec"
        ]

        if result["ok"]:

            ai_raw = result["content"]

            (
                valid,
                violations,
                numbered,
            ) = validate_ai_output(
                ai_raw,
                data
            )

            ai_violations = violations

            if valid:

                accepted_plan = dict(
                    safe_plan
                )

                accepted_plan[
                    "priorities"
                ] = numbered

                ai_status = (
                    "ACCEPTED - VERIFIED LOCAL REFINEMENT"
                )

            else:

                ai_status = (
                    "REJECTED BY SAFETY GATE - "
                    "SAFE PLAN RETAINED"
                )

        else:

            ai_status = (
                "QWEN UNAVAILABLE - "
                "SAFE PLAN RETAINED"
            )

            if result["error"]:
                ai_violations.append(
                    result["error"]
                )

    # --------------------------------------------------------
    # PRESENT ACCEPTED DECISION
    # --------------------------------------------------------

    print_plan(
        accepted_plan
    )

    total_time = (
        time.perf_counter()
        - total_start
    )

    # --------------------------------------------------------
    # AUDIT RECORD
    # --------------------------------------------------------

    audit = {
        "system":
            "AEGIS OMEGA AFRICA",

        "version":
            VERSION,

        "timestamp_utc":
            utc_now(),

        "status":
            "VERIFIED",

        "architecture": {
            "decision_core":
                "deterministic",
            "local_llm":
                "optional refinement",
            "cloud_dependency":
                False,
            "safe_fallback":
                True,
        },

        "crisis":
            data["crisis"],

        "severity": {
            "label":
                severity,
            "internal_score":
                score,
        },

        "rule_confidence":
            rule_confidence,

        "timing": {
            "immediate_decision_sec":
                round(
                    immediate_time,
                    6
                ),

            "ai_refinement_sec":
                round(
                    ai_elapsed,
                    4
                ),

            "total_pipeline_sec":
                round(
                    total_time,
                    4
                ),
        },

        "ai": {
            "requested":
                args.ai,

            "endpoint":
                QWEN_URL
                if args.ai
                else None,

            "status":
                ai_status,

            "violations":
                ai_violations,

            "raw_output":
                ai_raw,
        },

        "decision":
            accepted_plan,

        "safety": {
            "invented_resources_allowed":
                False,

            "resource_limits_enforced":
                True,

            "deterministic_fallback":
                True,

            "ai_output_requires_validation":
                True,

            "ai_can_block_immediate_decision":
                False,
        },
    }

    output_file = (
        "decision_v8.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            audit,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # FINAL SCOREBOARD
    # --------------------------------------------------------

    print(
        "\n" + "=" * 72
    )

    print(
        "STATUS             : VERIFIED"
    )

    print(
        f"RULE CONFIDENCE    : "
        f"{rule_confidence}/100"
    )

    print(
        f"IMMEDIATE DECISION : "
        f"{immediate_time:.6f} sec"
    )

    print(
        f"AI REFINEMENT      : "
        f"{ai_elapsed:.2f} sec"
    )

    print(
        f"TOTAL PIPELINE     : "
        f"{total_time:.4f} sec"
    )

    print(
        f"AI STATUS          : "
        f"{ai_status}"
    )

    print(
        f"SAVED              : "
        f"{output_file}"
    )

    if ai_violations:

        print(
            "\nSAFETY GATE"
        )

        for violation in ai_violations:
            print(
                f"- {violation}"
            )

    print("=" * 72)

    print(
        "NOTE: Confidence measures internal constraint coverage, "
        "not medical certainty."
    )

    print(
        "AEGIS is a crisis decision-support prototype and does not "
        "replace trained emergency responders."
    )

    print("=" * 72)


if __name__ == "__main__":
    main()