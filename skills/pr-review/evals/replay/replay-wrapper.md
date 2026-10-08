# Replay review

Read this whole file before any tool call. You are reviewing one pull request
at one historical commit. This is a replay: the result is written to disk and
nothing is posted. Work only from the workdir and the checked-out worktree.

Workdir: `{WORKDIR}`

- `diff.patch`: the full pull request diff from its base to the reviewed commit.
- `pr_body.md`: the PR title and body as they stood at review time.
- `issue.md`: the linked issue as it stood at review time, when one exists.
- `threads.json`: the review threads that existed on this PR before this review
  (path, line, is_resolved, author, excerpt). Earlier reviews of earlier commits.
- `head/`: a detached worktree of the reviewed commit. Every file read happens here.
- `state.json`: repo, PR number, reviewed SHA, base SHA.

Hard rules:

1. Never run `gh`, `curl`, `git fetch`, `git pull`, or anything that reaches
   the network.
2. Inside `head/`, `git log` and `git blame` are allowed only without `--all`
   and only to answer a specific question a hunk raised. Never `git show`,
   `checkout`, or `diff` a commit that is not an ancestor of `HEAD`.
3. Do not read any path outside the workdir. Do not open `/home/rehan/Projects`
   or any other directory under `/tmp/prreview-research`.
4. Do not edit, commit, or resolve anything.
5. Batch independent reads into one tool call. Read line ranges, not whole
   files, unless the file is under 200 lines.
6. Do not spawn subagents unless step 3 below requires a partition. If you
   partition, give each slice this whole file, use model `opus`, and say so in
   `record.md` with the slice list and the owner of each cross-slice dependency.

Deliverables. Write both files, then stop.

- `{WORKDIR}/findings.json`: a JSON array of objects with keys `path`, `line`,
  `severity`, `title`, `body`. `severity` is one of `P0`, `P1`, `P2`, `P3`.
  Include every admitted finding, P3 included. `path` is relative to `head/`.
  `line` is a line number in the new version of a file the diff touches.
  Empty array when nothing is admitted.
- `{WORKDIR}/record.md` with four sections. **Read plan**: the lines from
  step 3. **Candidates**: every candidate recorded in step 4 as anchor,
  trigger, actual result, expected result, evidence read, then `ADMIT` or
  `DROP`; a `DROP` names the contrary evidence you read (file and lines, or
  document section), never the absence of evidence.
  **Coverage check**: the step 6 result. **Budget**: your count of tool calls,
  the largest file-read batch, and whether the evidence overran the budget.

The method follows: steps 2 to 7 of the pr-review skill, then its severity
reference. Step 1 (gather) is already done for you, and step 8 (post) does
not run in a replay.

---

