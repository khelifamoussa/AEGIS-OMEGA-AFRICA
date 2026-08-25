# AEGIS OMEGA AFRICA V8 — Technical Report

## 1. Problem

AEGIS OMEGA AFRICA is an offline-first crisis decision-support prototype for environments where internet access, electrical power, compute capacity, and emergency-response resources may be limited.

The target use case is remote or infrastructure-constrained African communities affected by events such as flooding, wildfire, landslides, telecom outages, water contamination, village isolation, and mass-casualty incidents.

The central design requirement is that an emergency decision must not depend on cloud connectivity or on a generative model finishing successfully.

## 2. System Design

AEGIS uses a two-layer architecture.

### Deterministic safety core

The first layer validates structured scenario data and generates a safe baseline plan immediately. It performs input validation, internal crisis severity scoring, five deterministic priorities, resource-envelope preservation, critical-risk reporting, dependency reporting, explicit unknowns, and JSON audit output.

The deterministic plan is always available before any language-model refinement begins.

### Optional local LLM refinement

The second layer uses a local Qwen3-4B GGUF model through llama.cpp.

- Base model: Qwen3-4B
- Parameters: approximately 4.0B
- Quantization: GGUF Q4_K_M
- Runtime: llama.cpp
- Model file: `Qwen3-4B-Q4_K_M.gguf`

The local model is only a refinement layer. Its output is checked before acceptance. If it is unavailable, malformed, unsafe, or exceeds the configured timeout, AEGIS retains the deterministic plan.

## 3. Why Q4_K_M

Q4_K_M was selected as a balance between model quality and laptop constraints. The official Qwen3-4B GGUF repository lists the Q4_K_M artifact at approximately 2.5 GB, making it practical for the challenge's 8 GB RAM reference class while preserving useful model capability.

## 4. Constraints

The project was designed around:

- 8 GB RAM target hardware
- integrated graphics / CPU execution
- no cloud dependency during inference
- intermittent or absent internet connectivity
- scarce crisis resources
- strict avoidance of invented resource allocations
- fast deterministic fallback

## 5. Safety and Hallucination Controls

AEGIS does not automatically trust local LLM output. The safety layer checks invalid structure, incorrect action counts, unverified numeric values, invented resources, unsupported generator capabilities, unsupported satellite-phone capabilities, and overlong responses.

If validation fails, the original deterministic safe plan is retained.

## 6. Stress Testing

The V8 deterministic engine was tested across ten valid crisis scenarios and eight invalid-input cases.

Final local stress-test result:

```text
VALID CRISIS TESTS : 10/10 PASSED
INVALID INPUT TESTS: 8/8 PASSED
FAILED TESTS       : 0
FINAL STATUS       : STRESS TEST PASSED
```

The detailed machine-readable report is stored in `aegis_stress_results.json`.

## 7. Local Performance Observations

A final deterministic AEGIS V8 run on the development machine produced:

```text
STATUS             : VERIFIED
RULE CONFIDENCE    : 98/100
IMMEDIATE DECISION : 0.000064 sec
AI REFINEMENT      : 0.00 sec
TOTAL PIPELINE     : 0.0248 sec
AI STATUS          : DISABLED - DETERMINISTIC SAFE MODE
```

These figures measure the deterministic AEGIS application path and are not claimed as LLM inference latency.

Separate llama.cpp tests of the local Qwen3-4B Q4_K_M model produced generation speeds in roughly the 5–8 tokens/second range depending on prompt length and test configuration. A representative longer crisis prompt was approximately 5.3 tokens/second; a very short smoke test reached approximately 7.8 tokens/second.

Official profiler memory, thermal, and normalized challenge scores should be taken from the ADTC profiler run on the submission machine; they are not fabricated here.

## 8. Offline Operation

After the GGUF model is downloaded, inference is entirely local.

```bash
bash download_model.sh
```

The model is placed at:

```text
model/Qwen3-4B-Q4_K_M.gguf
```

## 9. Reproducibility

Deterministic mode:

```bash
python aegis_v8.py
```

Stress test:

```bash
python aegis_stress_test.py
```

Optional local model server:

```bash
llama-server -m model/Qwen3-4B-Q4_K_M.gguf -c 512 -t 8 --host 127.0.0.1 --port 8080
```

Optional AEGIS local-AI refinement:

```bash
python aegis_v8.py --ai
```

## 10. Limitations

AEGIS is a competition prototype and not a replacement for trained responders, professional medical judgment, official emergency procedures, or real-time field intelligence.

The internal rule-confidence value measures deterministic constraint coverage. It is not a medical certainty score or a probability of real-world outcomes.
