

# rehanhaider/naqid#181 @ 11f2849f5d — pr-review findings: 7

## 1. [P1] platform/packages/operations/src/scope-track-operations.ts:956
### Bound the overlap notice to its own 400-character contract
Bound the overlap notice to its own 400-character contract**

`ScopeTargetNotice.message` is capped at 400 characters (`scope-operations.ts:70`), but this template interpolates a Target literal that `TargetLiteral` allows up to 2048. One wildcard domain plus a URL Target under it whose literal exceeds 366 characters produces a longer message; `runOperation` then rejects the handler's own value against `contract.output` (`operations-route.ts:126`) and `statusForError` has no arm for it. `scope.get`, `track.list`, and every Scope mutation answer 500 for that Engagement, and the operator cannot delete the Target because the page no longer loads. `scope-import.ts:81` builds `reason` the same way against the same cap. Truncate the interpolated literal.
> REPLY (accepted): Fixed in 6db9562. `scopeTargetLabel` in `@naqid-cloud/schema/scope-target` bounds a quoted literal to 160 characters with an ellipsis, and both sentence builders use it — the overlap notice here and the `reason` in `scope-import.ts`. The displayed `existingDuplicate.literal` is left whole, because its own cap is 2048 and truncating it would change what the screen shows rather than what a sentence quotes.

Covered by `postgres-scope-track.test.ts` "quotes a long Target literal in a notice without breaking the answer", which puts a 1200-character URL under a wildcard domain and reads the Register back, and by a unit test that pins the worst-case sentence under 400.

## 2. [P1] platform/packages/clients-engagements/src/scope-repository.ts:348
### Chunk the bulk-import insert below the Postgres parameter limit
Chunk the bulk-import insert below the Postgres parameter limit**

`ApplyScopeImportInput.rows` accepts 10 000 rows, but they are written in one `insert().values()`. A target row binds 14 parameters, so 4 682 rows already exceed PostgreSQL's 65 535-parameter Bind limit, and at 10 000 rows drizzle 0.45.2 throws `RangeError: Maximum call stack size exceeded` before any SQL is sent. I measured both against the repository's own drizzle version. The Web import parser applies no row cap, so a 5 000-line target list previews cleanly and then fails the apply with an opaque error. Insert in batches, or lower `IMPORT_ROW_LIMIT` to what one statement can carry.
> REPLY (accepted): Fixed in 6db9562. `insertTargets` writes in batches of 500 rows inside the caller's transaction, so one statement binds 7000 parameters whatever the import size. Batching rather than lowering the limit: the limit is what an operator may paste, and it should not be set by a wire constraint.

Covered by `postgres-scope-track.test.ts` "writes an import larger than one insert statement can bind", which previews and applies 5000 rows against the real database — above the 4682 you measured.

## 3. [P2] platform/packages/operations/src/scope-track-operations.ts:788
### Delete the source Tracks before inserting the combined Track
Delete the source Tracks before inserting the combined Track**

This insert runs before the removal loop below it, against the non-deferrable `assessment_tracks_name_unique (engagement_id, lower(name))` index. Combining Tracks "A" and "B" into a Track the operator also calls "A" therefore fails with `track-name-taken`, naming a Track the same transaction was about to delete. The fixture source this workspace shipped against permits it deliberately: its combine passes the source ids to `normalizeName` as `ignoredTrackIds`. Move the `removeAssessmentTrack` loop above the insert.
> REPLY (accepted): Fixed in 6db9562. The sources are removed before the combined Track is inserted, so it may claim a source name. The identifiers are also deduplicated first, because the same Track named twice is one source.

Covered by the combine assertion in "combines Tracks into their union and splits references back out", which now combines into the name a source already held and passes a repeated identifier.

## 4. [P2] platform/apps/web/src/data/scope-control-plane-source.ts:765
### Give a client-side contract rejection a field and a sentence
Give a client-side contract rejection a field and a sentence**

When `callOperation` rejects the input against its Zod contract it returns `invalid-request` with no `fault`, so this fallback shows the operator "The track.create input did not match its contract." and no `field`. Submitting an empty Track name, an empty Scope Group name, or a combine with fewer than two Tracks now produces that developer prose instead of the fixture's "Enter an Assessment Track name.", and the input loses its `aria-invalid` marking. Map the contract-rejection reason to a field message before this branch.
> REPLY (accepted): Fixed in 6db9562. A blank Group or Track name is answered here with `field: "name"` and the sentence the fixture used — "Enter a Scope Group name." and "Enter an Assessment Track name." — before any request. The control plane still refuses it; this only decides which words reach the operator.

Covered by "asks for a Track name instead of sending one the contract would refuse", which also asserts that nothing was sent.

## 5. [P2] platform/packages/operations/src/scope-track-operations.ts:829
### Refuse a split that moves no references
Refuse a split that moves no references**

`referencesToMove` carries no minimum and nothing checks the resolved list, so a split with nothing selected creates a new empty Track, leaves the source untouched, and consumes the Engagement version. The dialog only disables submit while pending, and the fixture source refused exactly this with "Select one or more references from this Track." Reject an empty `moving` list here.
> REPLY (accepted): Fixed in 6db9562. `EmptyAssessmentTrackSplitError` refuses it as `track-split-empty`, mapped to 422 and to `validation` on the `references` field with "Select at least one Scope reference to move into the new Track."

Covered by a durable assertion in "combines Tracks into their union and splits references back out" and by the adapter test "marks a split that moves nothing on the references field".

## 6. [P2] platform/packages/operations/src/scope-track-operations.ts:945
### Stop the overlap scan being quadratic in container Targets
Stop the overlap scan being quadratic in container Targets**

Each entry filters every container, and each container then filters every entry, so cost scales with entries times containers. A Register of 4 000 IP-address Targets and 500 CIDRs — the shape bulk import exists for — took about 6.5 seconds of synchronous work when I timed these functions. It runs on `scope.get`, `track.list`, and every Scope and Track mutation response, blocking the API event loop for the whole process. Index the containers by host suffix and network prefix rather than comparing every pair.
> REPLY (accepted): Fixed in 6db9562. The pairs come from two indexes now: a hostname index (exact hostname, plus every parent suffix for wildcard containment) and an interval index for networks, sorted by start with a running highest end so an address stops scanning as soon as no earlier interval can reach it.

It also fixes pairs the container scan never found, which I had not noticed: two Targets that name one host in different forms — `https://app.example.test/x` and `app.example.test` overlap and neither contains the other — and one wildcard inside another. Both are pairs the fixture source discloses, so the container scan was a behaviour regression as well as a cost.

Covered by "names an overlap between 

## 7. [P2] platform/packages/operations/test/postgres-scope-track.test.ts:542
### Assert the Viewer read instead of swallowing it
Assert the Viewer read instead of swallowing it**

`.catch(() => undefined)` and the `if` below skip both assertions whenever the read throws, and `watcher` is never assigned to the Engagement: `engagementFor` creates it as `owner`, and `reachEngagement` refuses a non-Admin who holds no Membership. The only test behind the claim that a Viewer reads the whole Register therefore never runs its assertions, and a regression that denied Viewer reads would still pass green. Assign the Viewer in the fixture and assert unconditionally.
> REPLY (accepted): Fixed in 6db9562. The Viewer is assigned to the Engagement first, the `catch` is gone, and the read is asserted: the whole Register, `currentActor.role` of Viewer, `canManageScope` and `canManageTracks` both false, the write refused, and the Register unchanged afterwards. Without the assignment it would have proved a refusal for the wrong reason.


# rehanhaider/naqid#146 @ e50604afa8 — codex findings: 7

## 1. [P2] platform/apps/web/src/features/sessions/start-session-dialog.tsx:65
### Reload the Sessions list after a start conflict
Reload the Sessions list after a start conflict**

When `startSession` returns `version_conflict`, the fixture has advanced `concurrencyToken`, but this dialog only displays the error and provides no way to load the current Sessions. Each retry therefore sends the same stale token and fails again, although the message instructs the operator to load the current Sessions. Add a reload path that refreshes the workspace token while preserving the entered name.
> REPLY (unclear): Confirmed and fixed in 3c8bafb. The dialog now shows a **Load current Sessions** control on `version_conflict`, matching the `TrackDialog` precedent. It refreshes the workspace token, keeps the entered name, and clears the error so the retry uses the current token.

One extra defect surfaced while testing this: the reload flipped `workspaceState` to `loading`, which unmounted the dialog and cleared the name. `loadWorkspace` now takes a `silent` flag that keeps the ready layout mounted for a dialog-initiated reload.

Test: "reloads the Sessions token after a start conflict and keeps the entered name".

## 2. [P2] platform/apps/web/src/features/sessions/session-prompt-input.tsx:33
### Preserve a new Session draft when an old send completes
Preserve a new Session draft when an old send completes**

If a prompt for Session A remains pending, the operator can select Session B and type a new draft before A completes. The unmounted input for A still receives the successful result and calls this page-level callback, which clears B's new draft; the generation check in `SessionsPage.sendPrompt` prevents the stale detail update but does not change the returned success. Clear the draft only when the completed request still belongs to the active Session and original draft.
> REPLY (unclear): Confirmed and fixed in 3c8bafb. You are right that the generation guard I added earlier covered the detail write but not the draft clear. `SessionPromptInput` no longer clears the draft; `SessionsPage.sendPrompt` does it inside the same `detailGeneration` check, so a result that resolves after the selection moved leaves the new draft alone.

Test: "keeps a new Session draft when an earlier send completes".

## 3. [P2] platform/apps/web/src/features/sessions/session-conversation.tsx:57
### Do not label every Run Session as planless
Do not label every Run Session as planless**

For any Plan-guided Run Session, this unconditional Run-mode text states that the Session runs directly from the request and that no Plan guides it. Run mode supports both direct requests and accepted Plans, so the page will give operators false durable-state information unless the view model supplies the run type or the copy remains neutral.
> REPLY (unclear): Confirmed and fixed in 3c8bafb. AGENTS.md:50-51 states that Run mode "executes directly from the request without requiring a Plan, or follows a user-accepted Plan", so the old copy asserted a durable fact the view model does not carry. The copy is now neutral: "Run mode. This Session can run Tool Actions directly from the request or from an accepted Plan. Plan authoring is not in this view." A `runType` field belongs to #110, which owns Plan authoring.

Test: "states that a Run Session can follow an accepted Plan".

## 4. [P2] platform/apps/web/src/data/sessions-fixture-source.ts:557
### Snapshot the Track focus on each prompt
Snapshot the Track focus on each prompt**

When an operator sends a prompt under selected Tracks and later changes the Session focus, this entry retains only the text and author, so the earlier prompt has no focus revision or Track relationship that identifies its original context. This loses the Track attribution required by `PRODUCT_SPEC.md` INV-75 and makes later assessment provenance ambiguous. Store the current focus revision or relevant Track IDs with each prompt.
> REPLY (rejected): Confirmed and fixed in 3c8bafb. PRODUCT_SPEC.md INV-75 lists Prompts among the records that "retain their relevant Tracks", and CLAUDE.md makes PRODUCT_SPEC authoritative over the implementation plan, so the plan comment's entry union was wrong here. The `user-prompt` entry now carries `tracks`, snapshotted from the Session focus at send time, and every fixture prompt is seeded with the focus it was sent under. The conversation renders it as "Sent under: ...".

Test: "keeps the Track focus a prompt was sent under after the focus changes" asserts the earlier prompts are unchanged after the focus moves to a different Track.

## 5. [P2] platform/apps/web/src/data/sessions-fixture-source.ts:334
### Keep removed Track references out of editable checkboxes
Keep removed Track references out of editable checkboxes**

If Tracks that a Session selected or used are later removed, this projection keeps those historical IDs but does not expose their removed state, so the panel renders them as enabled checkboxes. The mutation then rejects every selected removed ID; with two retained removed selections, unchecking either one still submits the other and always fails, which prevents the operator from changing the focus. Mark retained references as unavailable, disable selecting them, and permit them to be removed from the current selection.
> REPLY (rejected): Confirmed and fixed in 3c8bafb. This was a real dead end: remove a Track in Scope and Tracks while a Session has it selected, and every later focus change failed validation.

`SessionTrackOptionViewModel` now carries `available`. A retained removed Track renders with a "No longer an active Track" badge, stays checkable only while it is selected (so it can be dropped), and `setSessionTrackFocus` accepts an id that is either an active Track or already in the current selection — so a removed Track can be kept or dropped but never selected again.

Test: "retains a removed Track in the selection and never lets it be selected again" removes `track-web` through the Tracks fixture first, then exerci

## 6. [P2] platform/apps/web/src/data/sessions-fixture-source.ts:415
### Update the Engagement summary when a Session is created
Update the Engagement summary when a Session is created**

Starting a Session adds it only to the separate Sessions fixture record. The shared fixture data source keeps the Engagement Details summary in `details[].sessions`, but this mutation never updates that projection, so navigating back to Engagement Details in the same fixture session shows the old Session count and omits the newly created durable Session. Derive both views from the Sessions owner or update the summary in the same operation.
> REPLY (accepted): Fixed in 3c8bafb, though not for the reason cited. D75 (AGENTS.md:206-210) argues the other way: Sessions owns the Session record, and `EngagementDetailsViewModel.sessions` is a summary projection of it. The plan comment for #109 also deliberately deferred the cross-projection write to #69/#73.

The stale Details glance was still a real inconsistency in the mock, so I took your second option: `startSession` notifies an injected `onSessionStarted` callback and `fixture-source.ts` appends the summary to the Details record. It does not bump the Details `version`, so an open Details editor keeps a valid `expectedVersion`. Deriving Details from the Sessions owner is the deeper fix and stays with 

## 7. [P2] platform/apps/web/src/features/sessions/sessions-page.tsx:172
### Refresh the rail summary after sending a prompt
Refresh the rail summary after sending a prompt**

After a successful send, the returned detail has `lastActivityAt` set to `Just now`, but this branch updates only `detail`; the rail continues to render the old `workspace.sessions` snapshot. The selected Session therefore shows a new prompt beside a stale last-activity value until the whole Sessions workspace is reloaded. Update the matching workspace summary from the mutation result or reload it after the send.
> REPLY (unclear): Confirmed and fixed in 3c8bafb. `applyMutation` now merges the returned session summary back into `workspace.sessions`, so the rail row for the selected Session updates its last activity, lifecycle, and turn together with the conversation. The `revision` field is stripped before the merge, since the rail model does not carry it.

Test: "refreshes the rail summary and prompt Tracks after a send" asserts the row moves from "05 Aug 2026, 09:31" to "Just now".


# rehanhaider/naqid#144 @ 20b4eed550 — codex findings: 3

## 1. [P2] platform/apps/web/src/features/assessment-tracks/assessment-tracks-panel.tsx:113
### Handle rejected Track removals
Handle rejected Track removals**

When the data source rejects this request because of a transport or server failure, the exception escapes from the void click handler as an unhandled promise rejection. The dialog stays open without an error message, so the operator cannot tell whether the Track was removed. Catch the rejection and set `mutationError`, as the other Track mutation paths do.
> REPLY (accepted): Fixed in 618b3ce. The removal handler now converts a rejected request into the existing dialog error state, keeps the dialog open for retry, and ignores stale completion; the new component test proves rejection and retry.

## 2. [P2] platform/apps/web/src/features/discovered-targets/discovered-targets-panel.tsx:87
### Handle rejected Discovered Target dismissals
Handle rejected Discovered Target dismissals**

When `dismissDiscoveredTarget` rejects because of a transport or server failure, this async handler has only `finally`, so the rejection becomes unhandled and the dismissal dialog shows no failure state. Catch the exception and populate `error` so the operator can retry instead of seeing a silent no-op.
> REPLY (accepted): Fixed in 618b3ce. The dismissal handler now converts a rejected request into the dialog error state, keeps the dialog open for retry, and ignores stale completion; the new component test proves rejection and retry.

## 3. [P2] platform/apps/web/src/features/coverage/coverage-panel.tsx:57
### Do not label Completed coverage as in progress
Do not label Completed coverage as in progress**

When a Completed Engagement retains any remaining coverage, this row still shows an `In progress` badge because it checks only `remaining > 0`. Completed Engagements are read-only, and completion does not imply that all unresolved work disappeared, so this label incorrectly tells the operator that assessment work is still underway. Show this badge only for an Open Engagement or use a status-neutral remaining-work label.
> REPLY (accepted): Fixed in 618b3ce. Coverage now uses the status-neutral label “Remaining work,” and the component test proves that a Completed Engagement with remaining coverage is not labelled “In progress.”


# rehanhaider/naqid#137 @ 5ce3656760 — codex findings: 6

## 1. [P2] platform/apps/web/src/data/fixture-source.ts:384
### Retain an Operator when an Admin creates an Engagement
Retain an Operator when an Admin creates an Engagement**

When an Admin creates an Engagement, `creatorMember` is undefined, so the new record starts with no assigned Operators. This violates the product requirement that every Engagement retain at least one Operator and lets the People tab show an invalid state immediately after creation. Create the record with a valid Operator assignment or require one as part of the Admin creation operation.
> REPLY (accepted): Fixed in 2d77388. Admin-created Engagement fixtures now assign a valid existing organization Operator, and a regression test verifies that the new Engagement retains that Operator.

## 2. [P2] platform/apps/web/src/features/engagement-details/engagement-details-page.tsx:89
### Clear Engagement data when conflict reload loses access
Clear Engagement data when conflict reload loses access**

If a concurrent change removes the current member or deletes the Engagement, the conflict reload returns `unavailable`, but this branch only shows a message and leaves the prior model in the ready state. The revoked user can continue to browse the cached Engagement tabs, and the old mutation controls remain visible. Clear the model and enter the unavailable state when this reload result occurs so future access ends immediately.
> REPLY (accepted): Fixed in 2d77388. An unavailable conflict reload now clears the cached model, enters the unavailable page state, and removes the old tabs and controls. A regression test covers access loss during recovery.

## 3. [P2] platform/apps/web/src/data/fixture-source.ts:418
### Number instruction revisions per Engagement
Number instruction revisions per Engagement**

This process-wide counter can make an Engagement skip revisions after instructions are edited elsewhere. For example, after two Meridian edits, the first edit to a new Engagement becomes revision 3 although revisions 1 and 2 never existed in that Engagement. This makes its immutable revision history report false sequence information; derive the next number only from `target.record.instructions.revision + 1`, as the other revisioned Web records do.
> REPLY (accepted): Fixed in 2d77388. The next instruction revision now comes only from the current Engagement revision plus one. A cross-Engagement regression test verifies that edits elsewhere cannot create gaps.

## 4. [P2] platform/apps/web/src/features/engagement-details/engagement-guidance.tsx:107
### Replace page errors when a mutation request throws
Replace page errors when a mutation request throws**

If an earlier mutation set the parent conflict or denial banner and the next instruction request rejects at the transport level, this catch updates only the Guidance-local message. The old page banner therefore remains beside the new network failure and continues to describe a failure that is no longer current. Report thrown failures to the parent, or clear its mutation error state before the request, and apply the same handling to the member and file request catches.
> REPLY (accepted): Fixed in 2d77388. Guidance, member, and file mutations now clear prior page-level mutation banners before each request, so a transport rejection leaves only the current local failure. Regression tests cover all three areas.

## 5. [P2] platform/apps/web/src/features/engagement-details/engagement-details-page.tsx:77
### Ignore stale retry results after route parameters change
Ignore stale retry results after route parameters change**

When a retry is pending and navigation changes this reused route to another Engagement, the parameter effect starts the new load but this unguarded retry can resolve later and overwrite it with the previous Engagement's model. The URL can then show one Engagement while the page exposes another Engagement's details. Use the same cancellation or request-generation guard as the initial effect before applying the retry result.
> REPLY (accepted): Fixed in 2d77388. Initial loads, retries, and conflict reloads now share a request-generation guard. A route-change regression test resolves the old retry after the new Engagement loads and verifies that it cannot replace the page.

## 6. [P2] platform/apps/web/src/data/fixture-source.ts:213
### Allow membership administration after Engagement completion
Allow membership administration after Engagement completion**

This blanket Completed-state rejection also blocks `addEngagementMember` and `removeEngagementMember`. A Completed Engagement still exposes its assessment record to assigned members, so an Admin must be able to revoke or grant that access without reopening the assessment and creating another Round. Apply the Completed read-only rule to assessment mutations such as guidance and files, but keep authorized membership administration available for every Engagement.
> REPLY (accepted): Fixed in 2d77388. Completed Engagements still deny guidance, file, and Session assessment changes, but Admins and assigned Operators can now manage membership access. Data-boundary and page tests verify this distinction.


# Mizanic/Qaleening#60 @ 954da55d6b — pr-review findings: 6

## 1. [P1] aws/src/fn/api/repositories/mosqueMembership.ts:512
### Let a re-approved SPOC be revoked a second time
Let a re-approved SPOC be revoked a second time**

The two `REVOKED` puts are conditioned on `attribute_not_exists(pk)`, and nothing ever deletes a `SPOC#REVOKED#<uid>` row (no TTL, per §7). So: revoke a SPOC, they re-request (the PENDING guards are on different keys), an approver approves (the APPROVED rows were deleted), then the admin revokes again — this put fails, DynamoDB cancels all five operations, and the route returns 409 "A revocation for this user and mosque already exists". The `SPOC#APPROVED#` row survives, so the user keeps passing `requireSpocOf`/`requireAdminOrSpocOf` with no API path left to remove them. Drop `attribute_not_exists` from both puts; the `attribute_exists` on the deletes already makes a double revoke a typed conflict.
> REPLY (accepted): Fixed in `5b65a75` — confirmed, and the guard bought nothing. The `attribute_exists(pk)` delete of the approved row already serialises the transaction, so `spocCount` could not double-decrement either way; all the condition did was make the second revocation of a re-admitted SPOC impossible. Both `REVOKED` puts are now unconditional. Regression test `can revoke the same person again after they are re-admitted` walks revoke -> re-request -> re-approve -> revoke and fails against the old condition.

## 2. [P2] aws/src/fn/api/routes/mosques.ts:847
### Let a re-filed request be rejected a second time
Let a re-filed request be rejected a second time**

This route is the first caller of `rejectSpocRequest`, which puts the `REJECTED` rows under `attribute_not_exists(pk)` and never deletes them. A rejected user may request again, but the second rejection can never commit — the row from the first is still there — so it 409s permanently. The re-filed request keeps its sparse `Q#SPOC_REVIEW` keys and sits in the global review queue forever; approving it is the only way an approver can clear it. Same fix as the revoke path: drop `attribute_not_exists` from the two `REJECTED` puts.
> REPLY (accepted): Fixed in `5b65a75` — same shape, same fix. The `REJECTED` puts are unconditional; `deletePendingMosqueSide`'s `attribute_exists(pk)` is what stops a request being decided twice. `can reject the same person again after they re-file` covers it.

## 3. [P2] aws/src/fn/api/routes/mosques.ts:748
### Seed the profile instead of 404ing the first membership request
Seed the profile instead of 404ing the first membership request**

`requireUserById` throws `NotFoundError` when no `USER#<id>/PROFILE` row exists, and profiles are created lazily by `GET /me` and `PATCH /me` only — there is no Cognito post-confirmation trigger. This is the repo's first route to hard-require that row, so a user who signs in and claims a mosque before any profile read gets `404 {"code":"NOT_FOUND"}`, the same code this route returns for a nonexistent mosque, and a client keying off `code` reports "mosque not found". Call `upsertUserProfileFromClaims` here as `GET /me` does, or give the missing-profile case its own code.
> REPLY (accepted): Fixed in `5b65a75`. It now seeds from the token claims when the profile row is absent, the same move `PATCH /me` already made, and 500s with `PROFILE_SEED_UNAVAILABLE` only when the claims cannot furnish one at all.

## 4. [P2] aws/test/routes/mosqueMemberships.test.ts:110
### Honour the transaction conditions in the fake, or drop the claim
Honour the transaction conditions in the fake, or drop the claim**

This docblock states that `attribute_exists`/`attribute_not_exists` "are honoured so a double decision fails the way DynamoDB would", but `applyTransaction` applies every Put and Delete unconditionally and never reads a `ConditionExpression`. No test in the file asserts a 409, so the conflict behaviour the PR lists as an acceptance criterion ("Duplicate pending request → 409") is unexercised — and the permanent-revocation and permanent-rejection failures above are invisible to this suite. Evaluate the conditions in the fake, or delete the sentence so the coverage claim matches what runs.
> REPLY (accepted): Fixed in `5b65a75`, and this is the finding that mattered most — the docblock was a claim the code did not honour, which is why both condition defects passed the suite. `applyTransaction` now evaluates `attribute_exists`/`attribute_not_exists` and throws the `TransactionCanceledException` shape the repository maps to a typed `ConflictError`.

## 5. [P2] aws/src/fn/api/routes/me.ts:132
### Return the rejection reason on the rejected user's own read path
Return the rejection reason on the rejected user's own read path**

`rejectMembershipBodySchema` makes `rejectionReason` mandatory because "the rejected party sees this", but it is written only to the mosque-side row; `UserMosqueLinkItem` has no such field, so this mapping cannot emit it. The mosque-side list accepts only `status=approved|pending` and gates `pending` to approvers, so a rejected requester has no route anywhere that returns their reason — producing exactly the support message the required field exists to prevent. Mirror `rejectionReason` (and `decidedByUserId`) onto the user-side row in `buildMembership`, or let the mosque-side list serve a caller their own rejected record.
> REPLY (accepted): Fixed in `5b65a75`. `rejectionReason` is mirrored onto the user-side row in `buildMembership` and returned here. A required reason that its only audience could never read was the contradiction; it is now on both halves.

## 6. [P2] aws/src/fn/api/routes/mosques.ts:850
### Validate :userId before it reaches a DynamoDB key
Validate :userId before it reaches a DynamoDB key**

`AGENTS.md` requires zod on "every request body, path param, and query param at the handler boundary", and `guards.ts` states a malformed path param is a 400 rejected "before the value reaches a key", warning that a long enough string "fails inside the SDK instead — a 500 for a bad request". All three decision routes (850, 869, 896) read `:userId` raw and pass it into `mosqueSpocLinkSk`/`userPk`, while `:mosqueId` on the same routes goes through `validateMosqueId`. An oversized `:userId` exceeds the sort-key limit and returns 500 `INTERNAL_ERROR` for a client error. Add a `userIdFrom` helper as `adminUsers.ts` already has.
> REPLY (accepted): Fixed in `5b65a75`. `subjectUserIdFrom` validates `:userId` as a Cognito sub (UUID) and 400s with `INVALID_PATH_PARAM`, applied before the authority check so the answer depends on what was wrong rather than on who asked — the ordering `BE-03` established for `:mosqueId`.


# Mizanic/Qaleening#53 @ e58238fb9d — codex findings: 10

## 1. [P1] aws/src/fn/api/routes/mosques.ts:140
### Honor idempotency keys before minting mosque IDs
Honor idempotency keys before minting mosque IDs**

When the client retries after the transaction succeeds but the response is lost, this handler calls `proposeMosque` again without honoring `Idempotency-Key` or supplying a stable `mosqueId`, so the retry mints and stores a second mosque. Claim and replay the repository's idempotency record before creating the proposal, as required for `POST /mosques`, to prevent duplicate pending or approved listings during transient network failures.
> REPLY (rejected): **Accepted** — fixed in b5ff2da. You are right and my earlier deferral was wrong.

I closed this same concern one round earlier by arguing idempotency was "cross-cutting work rather than part of mosque CRUD". That was a judgement made without reading `conventions-mobile.md` §2.5, which shows the client sending one *for this specific route*:

```ts
export const proposeMosque = (body: ProposeMosqueBody, idempotencyKey: string) =>
  request({ method: "POST", path: "/mosques", body, idempotencyKey, schema: mosqueSchema });
```

So it is this route's documented contract, not a general aspiration — and `repositories/idempotency.ts` already existed to honour it. Deferring meant shipping a route the

## 2. [P2] aws/src/fn/api/schemas/mosque.ts:43
### Reject city names that normalize to an empty slug
Reject city names that normalize to an empty slug**

When `address.city` contains only whitespace, this schema accepts it because `min(1)` counts the spaces, but `buildCityKey` subsequently strips them and stores the mosque under a malformed key such as `IN-KA-`. An admin submission is then immediately approved into that unbrowseable city partition, so trim and reject blank city names before deriving the index key.
> REPLY (unclear): **Accepted** — fixed in b5ff2da.

Confirmed the mechanism: `min(1)` counts whitespace, so `"   "` passed, and `buildCityKey` then stripped it to nothing and produced `IN-KA-`. Worse for an admin, whose submission is approved in the same request — straight into a partition nobody can browse, with no moderation step to catch it.

Trimmed before the length check, and applied to `street`, `state` and `country` too rather than only the field with the index consequence: they are all display strings where leading whitespace is a mistake, and fixing one of a set is how the next one is missed.

Test asserts a whitespace-only city is a 400 naming `address.city`.

## 3. [P2] aws/src/fn/api/schemas/mosque.ts:171
### Accept concise but valid rejection reasons
Accept concise but valid rejection reasons**

When an admin supplies a meaningful short reason such as `Duplicate`, the ten-character minimum returns 400 even though the moderation contract only requires a nonblank reason. This unnecessarily blocks valid decisions; trimming and requiring at least one character would reject empty input without excluding concise explanations.
> REPLY (unclear): **Accepted** — fixed in b5ff2da. `rejectionReason` is now `trim().min(1)`.

You are right that the ten was invented. The acceptance criterion says only that rejecting without a reason is a 400 and with one it is stored — I added a length floor on top of that and it rejected `Duplicate`, which is nine characters and a complete, accurate reason. Meanwhile ten characters of nonsense passed, so the rule was not even buying what it appeared to.

Trimming still rejects `""` and `"   "`, which is the property the criterion actually asks for.

Test now asserts `Duplicate` is accepted; the blank cases still 400.

## 4. [P1] aws/src/fn/api/routes/mosques.ts:92
### Return the mosque at the documented response root
Return the mosque at the documented response root**

Every successful single-mosque route returns `{ mosque: ... }`, but the documented mobile resource functions parse `GET /mosques/:id` and `POST /mosques` directly with `mosqueSchema`, whose root is the mosque object itself. Once the typed client replaces the mock, all of these successful responses will fail runtime contract parsing; return `toMosque(item)` directly or change the shared client contract consistently.
> REPLY (unclear): **Accepted** — fixed in b5ff2da, and this one would have broken every successful call.

`conventions-mobile.md` §2.5 is unambiguous once read:

```ts
export const getMosque = (id: string) =>
  request({ path: `/mosques/${encodeURIComponent(id)}`, schema: mosqueSchema });
```

`request` parses the response body with that schema at its **root**. My `{ mosque: … }` envelope would have failed contract parsing on `GET /mosques/{id}` and `POST /mosques` the moment the typed client replaced the mock — and because the client parses every response, it would have failed as a hard error rather than a missing field.

Single-mosque routes now return the mosque bare. The list keeps its envelope, because `

## 5. [P2] aws/src/fn/api/routes/mosques.ts:244
### Validate moderation path IDs before checking the admin role
Validate moderation path IDs before checking the admin role**

When a non-admin calls `/mosques/not-a-ulid/approve`, `requireAdmin()` rejects the request before `mosqueIdFrom` runs, producing a 403 instead of the required 400 `INVALID_PATH_PARAM`; the rejection route has the same ordering. Validate `:mosqueId` in middleware before the role decision so malformed paths have the same stable response for every authenticated principal.
> REPLY (rejected): **Accepted** — fixed in b5ff2da.

This is a rule `BE-03` spent a round establishing — a malformed path parameter is a **400**, a role failure a **403** — and `requireSpocOf` validates the id first for exactly that reason. Putting `requireAdmin()` in front on the moderation routes broke it back, and in the way that is hardest to notice: the response depended on *who asked* rather than on what was wrong, so an admin testing the endpoint saw the correct 400 and a non-admin saw 403.

A `validateMosqueId` middleware now runs before the role decision on both `approve` and `reject`. `PATCH` was already correct — `requireAdminOrSpocOf` validates internally.

Tests assert 400 for a malformed id as a 

## 6. [P2] aws/src/fn/api/schemas/mosque.ts:121
### Allow optional measurements to be cleared
Allow optional measurements to be cleared**

Once `carpetAreaSqFt`, `floors`, or `capacity` has been stored, the PATCH contract provides no way to remove an erroneous value: omission means unchanged, `null` is rejected, and zero is rejected as non-positive. Accept an explicit clearing representation such as `null` and translate it to a DynamoDB `REMOVE`, otherwise users must retain measurements they later determine are unknown.
> REPLY (rejected): **Accepted** — fixed in b5ff2da.

The trap is exactly as described: omission means unchanged, `0` fails `positive()`, and `null` was rejected — so a `carpetAreaSqFt` typed wrong was permanent. `BE-04` gave `phone` a `null`-clears affordance for precisely this reason, and I did not carry the lesson across.

`null` now clears `description`, `plusCode`, `carpetAreaSqFt`, `floors` and `capacity`.

**It needed a repository change, not just a schema one.** `updateMosqueDetails`'s `assign` only ever built `SET`, so passing `null` through would have stored a literal null — satisfying the write and then failing the response schema on every later read, which is worse than the gap. It now routes `null`

## 7. [P2] aws/src/fn/api/schemas/mosque.ts:53
### Reject the zero-coordinate placeholder
Reject the zero-coordinate placeholder**

A proposal with `coordinates: { latitude: 0, longitude: 0 }` passes these independent range checks and is stored as a mosque in the Gulf of Guinea, despite the schema comment explicitly intending the common `0,0` placeholder to produce a 400. Add a pair-level refinement rejecting that coordinate before it reaches the repository.
> REPLY (unclear): **Accepted** — fixed in b5ff2da, and the comment was the giveaway.

The schema's own docstring said "a transposed pair or a `0,0` placeholder is a 400" while the code did nothing of the kind: the two range checks are independent, `0` is inside both, and the mosque was stored in the Gulf of Guinea. A comment asserting a behaviour the code does not have is worse than no comment, because it stops the next reader looking.

A pair-level refine now rejects it, with the message pointing at `coordinates.latitude` so a form can highlight something.

Kept as its own rule rather than folded into the bounds, because `0,0` is not out of range — it is the value an uninitialised form field produces, which 

## 8. [P2] aws/src/fn/api/schemas/mosque.ts:94
### Accept the plus-code format already used by the product
Accept the plus-code format already used by the product**

When a user submits the locality-qualified Open Location Codes already present in `mobile/data/mosque.json`, this 20-character cap rejects every example: the existing values range from 28 to 62 characters. Because the mobile data is the declared de-facto mosque contract and these strings are used for navigation hand-off, remove or raise this undocumented limit rather than returning 400 for the product's own data format.
> REPLY (unclear): **Accepted** — fixed in b5ff2da. Raised to 120 characters, and trimmed.

I checked the product's own data rather than taking the range on trust: `mobile/data/mosque.json` carries four plus codes between **28 and 62** characters, e.g. `VH3M+G2P, South Avenue, Gottigere, Bengaluru, Karnataka 560083`. My 20-character cap rejected every one of them.

Worth naming what went wrong: the issue calls that file "the de-facto contract" and instructs the API to conform to it. I wrote a bound from an assumption about what a plus code looks like — the bare 11-character Open Location Code — without opening the file the issue points at. The locality-qualified form is what the product actually stores and wha

## 9. [P2] aws/src/fn/api/routes/mosques.ts:354
### Propagate edits to denormalized mosque links
Propagate edits to denormalized mosque links**

When an approved SPOC changes a mosque's name or address, this call updates only the `MOSQUE#.../META` item; existing `USER#.../MOSQUELINK#...` rows retain their denormalized `mosqueName`, `cityKey`, and `addressLine`. Since `listMyMosques` renders the default home view entirely from those link rows, every linked SPOC continues seeing stale details indefinitely unless this edit path also propagates or reconciles the mirrors.
> REPLY (partial): **Partially accepted** — the gap is real and confirmed; it is recorded on `BE-07` rather than built here.

Verified the mechanism: `UserMosqueLink` rows carry denormalised `mosqueName`, `cityKey` and `addressLine`, and `listMyMosques` renders the default home view entirely from them. So a rename through `PATCH /mosques/{id}` would leave every linked SPOC seeing the old details indefinitely — no read path reconciles them.

**Why not here.** No propagation helper exists, so this needs a new repository function that fans out across a mosque's SPOC links and updates each — a multi-row write with pagination and partial-failure semantics to design. The rows it would update are created by `BE-07`, 

## 10. [P2] aws/test/schemas/mosqueContract.test.ts:26
### Compare against the actual mobile schema
Compare against the actual mobile schema**

When `mobile/src/types/mosqueTypes.ts` adds, removes, or renames a field, this independently copied `MobileMosqueSchema` does not change, so the advertised drift test continues passing while the real mobile parser and API contract diverge. Import the actual schema in a cross-workspace contract test or move it to the planned shared-types package; comparing against a second handwritten copy cannot detect the drift this test claims to guard.
> REPLY (unclear): **Accepted** — fixed in b5ff2da. You are right that the test could not do the job it advertised.

I had documented the limitation in the file header and then written an assertion called "agrees with the mobile schema field for field" that compared a handwritten copy against a handwritten copy. Documenting a hole does not close it, and the name promised something the code could not deliver: edit `mosqueTypes.ts` and nothing here moves.

The drift case now reads `mobile/src/types/mosqueTypes.ts` **off disk**, extracts `MosqueSchema`'s field names, and compares three ways: the local copy must match the real source, every mobile field must exist on the API, and the API's extras must be exactly t
