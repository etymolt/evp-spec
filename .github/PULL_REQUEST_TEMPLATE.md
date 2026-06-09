## What this PR does

<!-- One paragraph. What changes and why. -->

## Section reference

<!-- If this touches the spec, name the affected section: §X.Y -->

## Kind of change

- [ ] Editorial — typo, prose clarity, link fix (lands in next patch release)
- [ ] Test vector — new vector + corresponding validator assertion
- [ ] Tooling — CI workflow, .github/ improvements, README polish
- [ ] Normative — requires precursor issue using `propose-normative-change` template

## Linked issue

<!-- Required for normative changes. -->

Closes #

## Validator status

```
pytest EVP-1-validator-tests.py -v
# expect 20/20 (or higher if you added vectors) passing
```

## Reviewers checklist

- [ ] Validator runs clean locally
- [ ] If touching the schema, schema validates all four Appendix B sample verdicts
- [ ] If touching the prose, the JSON Schema is updated in sync
- [ ] If touching `valid_until` or `axis_freshness`, the §11 temporal semantics still hold
- [ ] Voice: terse, declarative, citations where the prose makes a numeric or empirical claim
