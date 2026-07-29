---
name: compare_sources
track: core
kind: local_analysis
provider: ""
requires_env: []
inputs: [items, focus, max_sources]
outputs: [sources, source_count, common_terms, comparisons, limitations]
side_effect: false
---
# compare_sources

Compares source items already collected by another tool. It does not make
network requests and does not decide which source is true. The output is an
evidence aid showing overlap, per-source coverage, and missing metadata.
