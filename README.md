# AEGIS OMEGA AFRICA V8

**Offline, deterministic crisis decision-support for
connectivity-constrained environments**

AEGIS OMEGA AFRICA V8 is a competition prototype designed to produce an
immediate, auditable crisis-response plan on a standard laptop without
depending on cloud services. Its deterministic decision core prioritizes
safety constraints, rejects invalid scenarios, prevents resource
over-allocation, records key unknowns, and can optionally request a
local Qwen3 model refinement through llama.cpp.

## Why AEGIS

During floods, wildfires, infrastructure failures, remote-community
emergencies, and communications outages, cloud-dependent AI may become
unavailable exactly when decisions are most urgent.

AEGIS follows a **safe-first architecture**:

1.  **Immediate deterministic decision** --- produces the safe baseline
    without waiting for an LLM.
2.  **Constraint validation** --- checks scenario consistency and
    resource limits.
3.  **Optional local-AI refinement** --- uses a local Qwen3 model only
    when available.
4.  **Safety gate / fallback** --- if local AI fails, times out, or is
    unavailable, the verified deterministic plan is retained.
5.  **Audit output** --- saves decision metadata and timing to JSON.

## Competition Track

Primary fit: **Autonomous AI Agents / offline local orchestration and
privacy-focused decision support**.

The project is designed around the Africa Deep Tech Challenge
requirement for an end-to-end, on-device language-model solution that
can operate without cloud dependencies on the reference laptop class.

## Core Features

-   Fully local crisis decision core
-   No cloud dependency for the deterministic path
-   Fast immediate decision path
-   Deterministic safety constraints
-   Resource-allocation guardrails
-   Invalid-input rejection
-   Explicit critical dependencies
-   Explicit key unknowns instead of invented facts
-   Optional local Qwen3 refinement through llama.cpp
-   Safe fallback when the model is unavailable or exceeds the timeout
-   JSON audit trail
-   Multi-crisis stress-test suite

## Validated Stress Test

The final V8 package passed:

-   **Valid crisis scenarios:** 10/10
-   **Invalid input scenarios:** 8/8
-   **Failed tests:** 0
-   **Final status:** STRESS TEST PASSED

The detailed report is included as `aegis_stress_results.json`.

## Package Contents

``` text
AEGIS-OMEGA/
├── aegis_v8.py
├── aegis_stress_test.py
├── aegis_stress_results.json
├── decision_v8.json
├── README.md
├── requirements.txt
└── run_aegis.bat
```

## Requirements

### Deterministic mode

-   Windows 10/11
-   Python 3.10+ recommended
-   No cloud connection required

### Optional local-AI refinement

-   llama.cpp `llama-server.exe`
-   Local GGUF model used during development/testing:
    `Qwen3-4B-Q4_K_M.gguf`
-   llama.cpp server listening on `127.0.0.1:8080`

The model file and llama.cpp binaries are not bundled in this submission
package unless competition submission rules explicitly require them.

## Quick Start --- Recommended Safe Mode

Open Command Prompt inside the project folder and run:

``` cmd
python aegis_v8.py
```

This is the recommended emergency-response mode because the immediate
deterministic path does not wait for generative inference.

You can also double-click:

``` text
run_aegis.bat
```

## Optional Local-AI Refinement

Start llama.cpp from the directory containing `llama-server.exe` and the
GGUF model:

``` cmd
llama-server.exe -m "Qwen3-4B-Q4_K_M.gguf" -c 512 -t 8 --host 127.0.0.1 --port 8080
```

Verify the server:

``` cmd
curl http://127.0.0.1:8080/health
```

Expected response:

``` json
{"status":"ok"}
```

Then, from the AEGIS project folder:

``` cmd
python aegis_v8.py --ai
```

If Qwen is unavailable or exceeds the configured timeout, AEGIS retains
the deterministic safe plan.

## Stress Testing

Run:

``` cmd
python aegis_stress_test.py
```

Expected final summary for the validated package:

``` text
VALID CRISIS TESTS : 10/10 PASSED
INVALID INPUT TESTS: 8/8 PASSED
FAILED TESTS       : 0
FINAL STATUS       : STRESS TEST PASSED
```

The test suite writes:

``` text
aegis_stress_results.json
```

## Decision Output

AEGIS writes:

``` text
decision_v8.json
```

The audit record contains decision output and associated
validation/timing metadata produced by the program.

## Design Strategy

### Accuracy / Safety

Deterministic constraints and validation reduce unsafe allocation and
unsupported resource claims. Unknown information is explicitly
represented instead of silently invented.

### Performance

The immediate decision path is deterministic and does not wait for local
model generation.

### Efficiency

The deterministic core can operate without cloud infrastructure and
without a discrete GPU.

### Resilience

Local AI is an enhancement, not a single point of failure. The verified
baseline remains available when the local model is unavailable.

## Important Safety Notice

AEGIS is a **crisis decision-support prototype**. It does not replace
trained emergency responders, professional medical judgment, official
emergency procedures, or local authorities.

The displayed rule-confidence value measures internal constraint
coverage; it is **not medical certainty or real-world outcome
probability**.

## Project Status

**AEGIS OMEGA AFRICA V8 --- Competition Prototype**
