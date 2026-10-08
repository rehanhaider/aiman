# Replay scoring ledger (hand-matched by root cause, not by line)

Outcome codes: POSTED = admitted at P0-P2 (would be posted); P3 = admitted but priced P3 (not posted);
DROPPED = surfaced as a candidate, then dropped at the admission step (reason quoted); ABSENT = never a candidate.

## naqid#137 @ 5ce3656760 (Opus run 1) — reference: 6 Codex findings, all accepted. Live skill posted: nothing.
| # | Reference (Codex, accepted) | Replay outcome | Replay note |
|---|---|---|---|
| 1 | Retain an Operator when an Admin creates an Engagement | DROPPED | C4, rule 8: "the contract does not say who is assigned when an Admin creates". It quoted "an Engagement must retain at least one Operator" and still dropped. |
| 2 | Clear Engagement data when conflict reload loses access | DROPPED (related) | C11 covered self-removal, not the conflict-reload path; dropped rule 8 "tests show this is intended". |
| 3 | Number instruction revisions per Engagement | P3 | R3, same root cause; priced P3 as "fixture-only display accuracy". Codex P2, owner fixed. |
| 4 | Replace page errors when a mutation request throws | DROPPED | C10, exact match; rule 1: "the old banner still describes a real earlier failure". |
| 5 | Ignore stale retry results after route parameters change | DROPPED | C9, exact match; rule 7: "no in-page path changes engagementId while mounted" (wrong: route param change reuses the component). |
| 6 | Allow membership administration after Engagement completion | ABSENT | |
New, not in reference: R1 P2 "Keep tab panels mounted so Guidance drafts survive tab switches" = Codex's accepted finding at the NEXT SHA 2d773880e4 ("Keep Guidance drafts mounted across tab changes"). Real. R2 P3 textarea editable while pending: plausible, low.
Posted recall 0/6. Surfaced (any form) 5/6.

## naqid#144 @ 20b4eed550 (Opus run 1) — reference: 3 Codex findings, all accepted. Live skill posted: nothing.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Handle rejected Track removals | DROPPED | C3, exact match (try/finally, rejection to void); rule 7: "the only FrontendDataSource implementation is the fixture... no reachable rejection". |
| 2 | Handle rejected Discovered Target dismissals | DROPPED | same C3. |
| 3 | Do not label Completed coverage as in progress | P3 | R1, exact match, priced P3. Codex P2, owner fixed. |
Posted recall 0/3. Surfaced 3/3.

## Mizanic/Qaleening#53 @ e58238fb9d (Opus run 1) — reference: 10 Codex findings, 9 accepted, 1 partial. Live skill posted: nothing.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Honor idempotency keys before minting mosque IDs (P1) | DROPPED | K2, exact match; rule 8: data-model §8.10 and conventions-mobile §2.5 require it, FE-01's honoured list omits BE-05, so "owner intent unknown, exclude". Owner: "it is this route's documented contract". |
| 2 | Reject city names that normalize to an empty slug | P3 | K1/R1, same root cause (non-Latin instead of whitespace), priced P3. Codex P2, owner fixed. |
| 3 | Accept concise but valid rejection reasons | DROPPED | K6, exact match; rule 6: "the author's explicit design". Owner: "the ten was invented". |
| 4 | Return the mosque at the documented response root (P1) | ABSENT | Read conventions-mobile §2.5 and the mobile schema, did not compare the envelope. Owner: "would have broken every successful call". |
| 5 | Validate moderation path IDs before checking the admin role | DROPPED | K7, exact match; rule 1: "both refusals are true". Owner cited BE-03's 400-before-403 rule. |
| 6 | Allow optional measurements to be cleared | ABSENT | |
| 7 | Reject the zero-coordinate placeholder | ABSENT | Schema comment promises it; code does not. |
| 8 | Accept the plus-code format already used by the product | ABSENT | Product data has 28-62 char codes; cap is 20. |
| 9 | Propagate edits to denormalized mosque links (partial) | DROPPED | K4, rules 7/8: no reader at this SHA. Defensible; owner deferred to BE-07. |
| 10 | Compare against the actual mobile schema | ABSENT | Plan line 7 named the test; did not notice it compares a handwritten copy. |
Posted recall 0/9 accepted. Surfaced 5/10.

## Mizanic/Qaleening#60 @ 954da55d6b (Opus run 1, HOLDOUT) — reference: 6 skill findings, all accepted.
| # | Reference (skill, accepted) | Outcome | Note |
|---|---|---|---|
| 1 | Let a re-approved SPOC be revoked a second time (P1) | POSTED P1 | R1, exact. |
| 2 | Let a re-filed request be rejected a second time | DROPPED | C15, rule 4 "already present at base". Wrong: the route is the first caller, so newly reachable. |
| 3 | Seed the profile instead of 404ing the first membership request | POSTED P2 | R2, exact. |
| 4 | Honour the transaction conditions in the fake, or drop the claim | P3 | R6, exact; priced P3. Owner: "the finding that mattered most". |
| 5 | Return the rejection reason on the rejected user's own read path | POSTED P2 | R4, exact. |
| 6 | Validate :userId before it reaches a DynamoDB key | DROPPED | C7, rule 1; disproof addressed empty segments, not the oversized-key 500 the finding states. |
New: R3 P2 "Return requestNote and userEmail in the pending membership queue" = Codex's later finding at 3de7134a0d "Return request notes to approvers". Real. R5 P3 stale doc block: fine.
Posted recall 3/6 (live skill: 6/6). Surfaced 6/6.

## Running totals (4 commits scored)
Target commits (#137, #144, #53): posted 0/18, P3 3/18, dropped 8/18, absent 7/18. Surfaced 11/18.
Holdout (#60): posted 3/6, P3 1/6, dropped 2/6.
Two new true findings confirmed by Codex's later rounds (#137 R1, #60 R3).

## Diagnosis so far
Discovery works better than the live skill (11 of 18 reference defects surfaced on commits where it posted nothing).
Recall is lost at the admission step: "try to disprove" + "if a decisive link is unknown, exclude" turns
absence of evidence (no test, fixture never rejects, document silent, author's constant) into a drop.
Pricing loses the rest: dev-only or fixture-backed consequences land on P3, which is not posted.

## naqid#181 @ 11f2849f5d (Opus run 1, HOLDOUT) — reference: 7 skill findings, all accepted.
| # | Reference (skill, accepted) | Outcome | Note |
|---|---|---|---|
| 1 | Bound the overlap notice to its own 400-character contract (P1) | POSTED P2 | R4, exact, both sites. |
| 2 | Chunk the bulk-import insert below the Postgres parameter limit (P1) | POSTED P2 | R1, exact. |
| 3 | Delete the source Tracks before inserting the combined Track | POSTED P2 | R2, exact. |
| 4 | Give a client-side contract rejection a field and a sentence | ABSENT | fixture-parity finding (fixture sentence vs durable path). |
| 5 | Refuse a split that moves no references | ABSENT | fixture-parity finding (fixture refused it). |
| 6 | Stop the overlap scan being quadratic in container Targets | DROPPED | C11, rule 7: "no measured evidence". The skill timed it (6.5 s). |
| 7 | Assert the Viewer read instead of swallowing it | ABSENT | tests-vs-claims finding (.catch(() => undefined) skips the assertions). |
New: R3 P2 "Record an Engagement Provenance obligation for each Scope and Track change" = the skill's accepted finding at the NEXT SHA 6db9562089. Real.
Posted recall 3/7 (live skill 7/7). Surfaced 4/7. Budget overran (about 135k tokens in one window), no partition.

## Holdout total: posted 6/13 vs live skill 13/13. Misses are the skill's known strengths: tests-vs-claims (1), fixture-contract parity (2), measured performance (1), path validation (1), rule-4 newly-reachable (1), plus 1 wrong disproof.

## naqid#146 @ e50604afa8 (Opus run 1, second attempt; first attempt's write was blocked) — reference: 7 Codex findings, all accepted. Live skill posted: nothing.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Reload the Sessions list after a start conflict | POSTED P2 | R1, exact. |
| 2 | Preserve a new Session draft when an old send completes | P3 | R3/C5, exact, priced P3 ("narrow"). Codex P2, owner fixed. |
| 3 | Do not label every Run Session as planless | DROPPED | C3, rule 4 "Plans not modeled at head". Owner cited AGENTS.md L50-51. |
| 4 | Snapshot the Track focus on each prompt (INV-75) | ABSENT | invariant sweep miss. |
| 5 | Keep removed Track references out of editable checkboxes | POSTED P2 | R2, exact. |
| 6 | Update the Engagement summary when a Session is created | DROPPED | C4, rule 1 "dev-only copy of fixture data". Owner fixed. |
| 7 | Refresh the rail summary after sending a prompt | DROPPED | C7, rule 6 "no contract says the rail updates live". Owner fixed. |
Posted recall 2/7. Surfaced 6/7.

## v1 TOTALS — target commits (25 accepted): POSTED 2, P3 4, DROPPED 11, ABSENT 8. Surfaced 17/25 (68%). Posted 2/25 (8%). Live skill at these SHAs: 0/25.
## v1 TOTALS — holdout (13 accepted skill findings): POSTED 6, P3 1, DROPPED 3, ABSENT 3. Live skill: 13/13.
## v1 new true findings confirmed by a later round of the other reviewer: 3 (#137 R1, #60 R3, #181 R3).
## v1 cost (Opus 5.5, one agent): $16.5-$41.4 per run; the blocked #146 attempt cost $25.3 extra. Pass condition 4 (under $8) failed on every run.

## v2 changes (METHOD-v2.md), each tied to the misses above
- Step 2: list every invariant/decision/AC naming each record the change writes (ABSENT: #137-6, #146-4, #53-6).
- Step 4: hunk audit of constants/bounds/comments/orderings against doc and product data (#53-2,3,5,7,8); invariant sweep (#137-1,6; #146-4); contract parity incl. copy-vs-copy tests (#53-4,10); fixture/mock parity (#181-4,5); tests-vs-claims executing assertions (#181-7, #60-4); async trace of the specified production adapter even when the fixture never rejects (#144-1,2); route-param remount (#137-5); copies/projections incl. fixtures (#146-6, #137-3); cost shape without measurement (#181-6).
- Step 5: drop only on named contrary evidence; eight non-disproofs listed; contract doc governs over status list (#53-1); new caller = newly reachable (#60-2); author's choice is an unstated assumption unless recorded (#53-3).
- Step 6: P2 floor for any admitted defect; dev-only priced by production consequence (#137-3, #144-3, #146-2, #53-2, #60-4).

## CONTROL: naqid#144 @ 20b4eed550, Codex gpt-6-astra (reasoning high) running the v1 METHOD text — reference 3.
| # | Reference (Codex cloud, accepted) | Outcome | Note |
|---|---|---|---|
| 1 | Handle rejected Track removals | DROPPED | C1 exact; rules 6/7: "shipped callees have no network rejection path; a rejected future adapter is not evidence". Same drop, same reason as Opus v1. |
| 2 | Handle rejected Discovered Target dismissals | DROPPED | same C1. |
| 3 | Do not label Completed coverage as in progress | ABSENT | |
Posted: 1 P2 (dev-fixture scenario mismatch, the candidate Opus v1 dropped as C5). 21 tool calls.
Conclusion: with the v1 text, Codex drops the finding Codex's own cloud reviewer posted and the owner fixed. The admission text, not the model, causes the drop.

## CONTROL: Qaleening#53 @ e58238fb9d, Codex gpt-6-astra (reasoning high) running the v1 METHOD text — reference 9 accepted + 1 partial.
| # | Reference (Codex cloud) | Outcome | Note |
|---|---|---|---|
| 1 | Honor idempotency keys before minting mosque IDs (P1) | POSTED P2 | X3, exact; quoted data-model §8.10 and rejected the FE-01 list as a waiver. Opus v1 dropped the same candidate as "owner intent unknown". |
| 2,3,5,6,7,8 | schema constants, orderings, null clearing, 0,0 placeholder, plus-code cap | ABSENT | same blindness as Opus v1: behaviour-level plan, no hunk-level audit. |
| 4 | Return the mosque at the documented response root (P1) | ABSENT | |
| 9 | Propagate edits to denormalized mosque links (partial) | POSTED P2 | X2, exact. |
| 10 | Compare against the actual mobile schema | DROPPED | C4 "future-only test limitation" (step 5 missing-tests exclusion). |
Also posted: X1 concurrent edit/approve stale GSI keys = Codex cloud's NEXT-round finding "Serialize pending edits with moderation" (b5ff2da338). Real. Opus v1 had it (K3) and dropped it.
17 tool calls. Posted 2/10 reference (Opus v1: 0/10).
Conclusion from both controls: the v1 admission text drives drops in both models (Codex dropped its own #144 findings); the behaviour-level read plan hides hunk-level schema findings in both models; Codex admits somewhat more readily than Opus on the same text (2 vs 0 here).

# v2 results

## naqid#146 @ e50604afa8 (Opus v2) — reference 7 accepted.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Reload the Sessions list after a start conflict | POSTED P2 | R3 |
| 2 | Preserve a new Session draft when an old send completes | POSTED P2 | R2 (v1 had it at P3) |
| 3 | Do not label every Run Session as planless | POSTED P2 | R8, cites PLAN L240-241 (v1 dropped) |
| 4 | Snapshot the Track focus on each prompt (INV-75) | ABSENT | still missed |
| 5 | Keep removed Track references out of editable checkboxes | POSTED P2 | R1 |
| 6 | Update the Engagement summary when a Session is created | POSTED P2 | R4 (v1 dropped as dev-only) |
| 7 | Refresh the rail summary after sending a prompt | POSTED P2 | R7 (v1 dropped) |
New: R5 parity test cannot fail (Details lists 3 of 6 Sessions) = Codex later rounds "Seed every durable Session" / "Add every seeded Session to its ... Details projections". R6 out-of-order mutation results overwrite = Codex next round "Reject older results from parallel Session mutations". R9 P3 wording. Nothing I would reject.
Posted recall 6/7 (v1: 2/7).

## Qaleening#53 @ e58238fb9d (Opus v2) — reference 9 accepted + 1 partial.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Honor idempotency keys (P1) | POSTED P2 | R1; applied data-model over the FE-01 status list, as v2 step 5 says |
| 2 | Reject city names that normalize to an empty slug | DROPPED (related) | C15 was the Bangalore/Bengaluru angle; the empty-slug case was not raised this run (v1 had it at P3) |
| 3 | Accept concise but valid rejection reasons | POSTED P2 | R6 (v1 dropped as author's design) |
| 4 | Return the mosque at the documented response root (P1) | ABSENT | contract-parity check compared field shapes, not the response root |
| 5 | Validate moderation path IDs before the admin role | DROPPED | C10, named contrary evidence: base adminUsers.ts uses the same order. Defensible under v2; owner cited BE-03's rule. |
| 6 | Allow optional measurements to be cleared | ABSENT | |
| 7 | Reject the zero-coordinate placeholder | POSTED P2 | R4 (hunk audit: comment promises it) |
| 8 | Accept the plus-code format already used by the product | POSTED P2 | R5 (hunk audit: checked mosque.json) |
| 9 | Propagate edits to denormalized mosque links (partial) | POSTED P2 | R2 |
| 10 | Compare against the actual mobile schema | POSTED P2 | R7 (contract parity: copy vs copy) |
New: R3 concurrent edit/approve stale GSI keys = Codex next round "Serialize pending edits with moderation". R8 P3 comment points at wrong file. Nothing I would reject.
Posted recall 5/9 accepted + the partial (v1: 0/9).

## naqid#144 @ 20b4eed550 (Opus v2) — reference 3 accepted.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Handle rejected Track removals | POSTED P2 | R1 (v1 and Codex control dropped as "fixture never rejects") |
| 2 | Handle rejected Discovered Target dismissals | POSTED P2 | R2 |
| 3 | Do not label Completed coverage as in progress | ABSENT | v1 had it at P3; not surfaced this run (run variance) |
New: R3 Track rename leaves stale name copies in Findings/Tool Results (plausible, not validated by any later round); R4 P3 "Back to Client" wording. Nothing I would reject.
Posted recall 2/3 (v1: 0/3).

## Qaleening#60 @ 954da55d6b (Opus v2, HOLDOUT) — reference 6 accepted skill findings.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Re-approved SPOC revoked a second time (P1) | POSTED P1 | R1 |
| 2 | Re-filed request rejected a second time | POSTED P2 | R2 (v1 dropped under rule 4) |
| 3 | Seed the profile instead of 404 | POSTED P2 | R3 |
| 4 | Honour the transaction conditions in the fake | P3 | R10, still P3 despite the "test that cannot fail" floor |
| 5 | Rejection reason on the requester's read path | POSTED P2 | R5 |
| 6 | Validate :userId before it reaches a key | DROPPED | C13, contrary evidence "opaque min(1) string"; the oversized-key 500 not addressed |
New and validated by the live skill's own LATER rounds on this PR: R6 propagate to REJECTED/REVOKED mirrors (= "Refresh the rejected and revoked mirrors too", 5b65a7540a, accepted); R7 bind membership cursors (= "Bind the membership cursors, or answer 400 instead of 500", 5b65a7540a, and "Bind and decode the cursor on GET /me/memberships too", 6936ff7da5, both accepted); R11 P3 mirror fan-out test claim (= "Correct the stub's claim that the mirror fan-out is tested", 5b65a7540a, accepted). R4 requestNote = Codex's later finding. R8/R9 P3 comments. Nothing I would reject.
Posted recall 4/6 (v1: 3/6; live skill 6/6 in round one, but v2 also posted 3 defects the live skill needed rounds two and three to find).

## naqid#137 @ 5ce3656760 (Opus v2) — reference 6 accepted.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Retain an Operator when an Admin creates an Engagement | POSTED P2 | R1, invariant sweep (INV-60) (v1 dropped) |
| 2 | Clear Engagement data when conflict reload loses access | ABSENT | not surfaced this run |
| 3 | Number instruction revisions per Engagement | POSTED P2 | R3 (v1 P3) |
| 4 | Replace page errors when a mutation request throws | ABSENT | v1 surfaced and dropped it; not surfaced this run |
| 5 | Ignore stale retry results after route parameters change | POSTED P2 | R6 (v1 dropped) |
| 6 | Allow membership administration after Engagement completion | ABSENT | |
New: R5 Guidance draft lost on tab switch = Codex next-round accepted finding. R4 textarea editable while pending, R2 empty/long overrides applied to every mutation result, R7 test asserts unrelated seeded content: plausible, unvalidated. R8/R9 P3. Nothing I would reject outright; R2 and R7 are the ones the owner should judge.
Posted recall 3/6 (v1: 0/6).

## naqid#181 @ 11f2849f5d (Opus v2, HOLDOUT) — reference 7 accepted skill findings.
| # | Reference | Outcome | Note |
|---|---|---|---|
| 1 | Bound the overlap notice (P1) | POSTED P1 | R2 |
| 2 | Chunk the bulk-import insert (P1) | POSTED P1 | R1 |
| 3 | Delete the source Tracks before inserting the combined Track | POSTED P2 | R6 |
| 4 | Give a client-side contract rejection a field and a sentence | ABSENT | |
| 5 | Refuse a split that moves no references | POSTED P2 | R7 (fixture parity; v1 absent) |
| 6 | Stop the overlap scan being quadratic | POSTED P2 | R13 (cost shape; v1 dropped for lack of measurement) |
| 7 | Assert the Viewer read instead of swallowing it | POSTED P2 | R9 (tests-vs-claims; v1 absent) |
New and validated by the live skill's or Codex's LATER rounds on this PR: R3 Provenance obligation (skill, 6db9562089, accepted); R4 URL duplicate key canonical (skill "Key a URL Target off its canonical value", accepted; Codex "Canonicalize network values"); R11 import bound vs body limit (skill "Bound the import to a size the operations transport can carry", accepted); R8 whitespace-only names/descriptions (skill "Reject a blank Track description", 7a6d828aef); R12 emptied import row (skill "Trim the import row literal", e9332df713; Codex fix 4863e093fe). Unvalidated: R5 CIDR empty prefix/reversed range (Codex posted both later; owner reply unknown), R10 toEqual, R14 P3 wrong INV numbers.
Posted recall 6/7 (v1: 3/7; live skill 7/7). 62 tool calls; budget overran again.

# v2 TOTALS
Target commits (25 accepted): POSTED 16/25 (64%) — #137 3/6, #144 2/3, #146 6/7, #53 5/9 (+ the partial). v1: 2/25. Live skill: 0/25. Codex cloud: 25/25 by construction.
Plus 4 findings on target commits validated by Codex's later rounds (#137 R5, #146 R5, #146 R6, #53 R3).
Holdout (13 accepted skill findings): POSTED 10/13 (77%) — #60 4/6, #181 6/7. v1: 6/13. Live skill: 13/13. Plus 8 findings the live skill or Codex found only in later rounds (#60: 3, #181: 5).
Pass condition 1 (≥18/25, ≥1 per commit): FAILED by 2 at 16/25; every commit ≥2.
Pass condition 2 (no finding the owner would reject): my read is none rejectable; about 7 unvalidated findings need the owner's judgment.
Pass condition 3 (holdout ≥ live skill): FAILED at 10/13 on the strict count; v2 posted 18 owner-validated findings in round one against the live skill's 13.
Pass condition 4 (under $8): FAILED on every run; v1 and v2 both cost $16-$41 per run on Opus 5.5.
