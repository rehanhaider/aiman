# Recall corpus

`../evals.json` measures whether the skill *labels and posts* correctly. It
cannot measure whether the skill *finds* anything, because every case states the
defect in the prompt. This corpus measures detection.

## Why it exists

On `Mizanic/Qaleening#50` at `68875d40a9`, the skill posted "no findings." Seven
minutes later an independent reviewer posted four findings on the same commit,
all of which the repository owner accepted. Nothing in the eval suite could have
caught that, and nothing in the skill's own output revealed it.

Three of those four defects were in files the skill never opened: it had scoped
the pass to the newest commit's three files rather than the pull request's
eleven. That is now forbidden in `SKILL.md` §2, and this corpus is how the fix
gets verified instead of assumed.

## What is in it

`ground-truth.json` holds findings that were posted to real pull requests and
accepted by the owner — so each one is a defect a competent review should have
found. Both reviewers contribute, which matters: a corpus built from one
reviewer would encode that reviewer's blind spots as the definition of success.

Rebuild it after more dual-reviewed PRs accumulate:

```bash
python3 build_ground_truth.py > ground-truth.json
```

## Using it

```bash
python3 score.py --coverage

python3 <skill>/scripts/pr_review.py gather 50 --repo Mizanic/Qaleening
# ...run the review, write findings.json, do not post...
python3 score.py --findings findings.json --repo Mizanic/Qaleening --pr 50
```

Exit code 1 means a P1 or P2 in the corpus was missed.

Score against the whole pull request, not a single SHA. The two reviewers
anchored at different commits, so `--sha` splits them apart; it is for narrow
analysis, not for grading a review.

## Reading a score honestly

**Matching is generous by design.** Same file plus a near-exact line, or same
file plus overlapping wording within 40 lines. A generous matcher overstates
recall, which is the safe direction: a low score is trustworthy, and a high one
still needs you to confirm the matches are the same defect. Under-counting would
be worse, since it would send you hunting for findings the review already made.

**"Not in corpus" is not a false positive.** It is a finding nobody has judged.
The skill finding something new is the point — several corpus entries are
defects one reviewer found and the other missed entirely.

**Recall of 100% is not the goal, and this corpus cannot certify quality.** It
is 42 findings from three pull requests in three repositories. It is enough to
catch a regression of the kind described above; it is not a benchmark. Treat a
falling score as evidence and a rising score as a hypothesis.

**Do not tune the prompt until this corpus passes.** That is overfitting to 42
examples. Use it to detect the specific failure of reviewing less than the whole
pull request, and to check that a change meant to raise recall did not instead
raise noise — the "not in corpus" list is where noise shows up first.
