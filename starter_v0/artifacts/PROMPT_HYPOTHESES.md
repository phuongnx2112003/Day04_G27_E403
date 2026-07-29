# Prompt and routing hypotheses

## v1 evidence

- Run: `runs/v1_B_base_openai_20260729T103707406239.json`
- Provider/model: OpenAI / gpt-4o-mini
- Total and measured cases: 20 / 20
- Provider errors: 0
- Passed cases: 19
- Case accuracy: 0.9500
- Tool routing accuracy: 0.9500
- Argument accuracy: 0.9500
- Multi-turn accuracy: 0.8333
- Only failure: `M06_switch_tool`
- Observed mismatch: extra `social_search` call after the user cancelled
  Twitter and switched to web news.

## v2 hypothesis

- Changed artifact: `artifacts/system_prompt.md`
- Change: make an explicit tool/source cancellation persistent across later
  turns. A later topic/count/timeframe refinement must not reactivate a
  cancelled tool.
- Hypothesis: `M06_switch_tool` will call only `lookup`, while the 19 passing
  cases remain unchanged.
- Metric target: improve case accuracy from 0.9500 to 1.0000 and multi-turn
  accuracy from 0.8333 to 1.0000.
- No tool implementation or eval case change is justified by the v1 evidence.

## v2 result

- Run: `runs/v2_B_base_openai_20260729T111304740269.json`
- Provider errors: 0
- Measured cases: 20 / 20
- Passed cases: 19
- Case accuracy: 0.9500
- Multi-turn accuracy: 0.8333
- `M06_switch_tool` still called both `lookup` and `social_search`.
- Conclusion: the cancellation rule at the end of the prompt was weaker than
  the broad parallel-tool rule and the vague tool descriptions.

## v3 hypothesis

- Changed artifacts: `artifacts/system_prompt.md` and `artifacts/tools.yaml`
- Change: apply cancellations before tool selection; parallel calls require
  multiple sources in the final active request; clarify that `social_search`
  is unavailable after social media is cancelled.
- Hypothesis: the model will call only `lookup` for the remaining v2 failure
  while preserving the 19 passing cases.
- Metric target: case accuracy and multi-turn accuracy both reach 1.0000.

Do not fill v3 after-metrics until a real provider run completes with
`provider_error_cases=0` and `measured_cases=total_cases`.
