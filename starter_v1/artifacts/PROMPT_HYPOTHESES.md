# Prompt and routing hypotheses

## v0 baseline evidence

- Provider/model: OpenAI / gpt-4o-mini.
- Total cases: 20.
- Provider errors: 0.
- Passed cases: 14.
- Case accuracy: 0.7000.
- Tool routing accuracy: 0.7500.
- Argument accuracy: 0.7000.
- Multi-turn accuracy: 1.0000.
- Failures: `R08`, `R10`, `R11`, `R12`, `R13`, `R14`.
- `R08` and `R14`: an out-of-scope request triggered `send`.
- `R10` and `R11`: missing account/URL triggered a data tool instead of
  `clarify`.
- `R12`: `send` was called without confirmation.
- `R13`: both tools were selected, but the lookup arguments were wrong.

## v1 hypothesis

- Changed prompt: `artifacts/system_prompt.md`.
- Change: add a narrow safety guardrail for scope, missing information, and
  external-send confirmation.
- Expected improvement: `R08`, `R10`, `R11`, `R12`, and `R14`.
- Deliberately deferred: `R13` routing and argument normalization belongs to
  a later routing iteration.
- Baseline metric: `case_accuracy=0.7000`.
- Do not fill the v1 after-metric until a real v1 provider run is complete.

## Tool deliverable

`compare_sources` is added as the required new local tool. It does not change
the v1 hypothesis and is not expected to affect the base cases unless a user
asks for source comparison.
