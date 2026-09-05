"""Tests for the verdict logic — the one function that can emit a false clean."""

from __future__ import annotations

import unittest

from pr_watch import (
    DEFAULT_SIGNATURE,
    EXTERNAL_REVIEWER_PROFILES,
    check_result_line,
    clean_marker_sha,
    comment_attestation,
    grade_check_run,
    parse_review_id,
    resolve_verdict,
    reviews_missing_marker,
    verdict_for,
)

HEAD = "9272601754ee1b5c6209649b4753b76680d91d83"
CLEAN_BODY = f"Reviewed `{HEAD[:10]}` — no new issues found."
# What pr_review.py post renders around the verdict line.
NOTE = "> [!NOTE]\n> 🤖 Reviewed by Claude/Opus-5\n\n"
HIDDEN = f"\n\n<!-- {DEFAULT_SIGNATURE} -->"
BUGBOT = next(p for p in EXTERNAL_REVIEWER_PROFILES if p["name"] == "cursor-bugbot")


def review(body: str, *, sha: str = HEAD, author: str = "reviewer", state: str = "COMMENTED") -> dict:
    return {"body": body, "commit_id": sha, "author": author, "state": state, "url": ""}


def snapshot(reviews: list[dict], *, warning: str | None = None) -> dict:
    return {"reviews": reviews, "threads": [], "comments": [], "warning": warning}


def thread(*, resolved: bool = False, outdated: bool = False) -> dict:
    return {"is_resolved": resolved, "is_outdated": outdated}


class TestCleanMarker(unittest.TestCase):
    def test_exact_sentence_matches_and_returns_sha(self):
        self.assertEqual(clean_marker_sha(CLEAN_BODY), HEAD[:10])

    def test_objection_containing_the_words_is_not_clean(self):
        for body in (
            "No major issues in the happy path, but the retry loop needs a rethink.",
            "I would not say there are no findings here — see my comments.",
            "no new issues found in the API, but the migration is unsafe.",
            "LGTM",
            "",
        ):
            with self.subTest(body=body):
                self.assertIsNone(clean_marker_sha(body))

    def test_marker_must_be_the_first_line(self):
        body = f"This PR worries me.\n\n{CLEAN_BODY}"
        self.assertIsNone(clean_marker_sha(body))

    def test_accepts_hyphen_and_trailing_whitespace(self):
        self.assertEqual(clean_marker_sha(f"Reviewed `{HEAD[:10]}` - no new issues found.  "), HEAD[:10])

    def test_leading_reviewer_note_is_skipped(self):
        self.assertEqual(clean_marker_sha(NOTE + CLEAN_BODY + HIDDEN), HEAD[:10])

    def test_plain_quote_before_the_marker_is_not_an_alert(self):
        self.assertIsNone(clean_marker_sha("> looks fine to me\n\n" + CLEAN_BODY))

    def test_note_alone_is_not_a_verdict(self):
        self.assertIsNone(clean_marker_sha(NOTE.strip()))

    def test_prose_between_note_and_marker_is_rejected(self):
        self.assertIsNone(clean_marker_sha(NOTE + "Some concerns.\n" + CLEAN_BODY))


class TestReviewsMissingMarker(unittest.TestCase):
    def test_all_clear_from_every_author_passes(self):
        at_head = [review(CLEAN_BODY, author="a"), review(CLEAN_BODY, author="b")]
        self.assertEqual(reviews_missing_marker(at_head, HEAD), [])

    def test_one_objector_is_not_outvoted_by_a_later_clean_review(self):
        at_head = [review("This breaks auth.", author="b"), review(CLEAN_BODY, author="a")]
        missing = reviews_missing_marker(at_head, HEAD)
        self.assertEqual([r["author"] for r in missing], ["b"])

    def test_author_latest_review_supersedes_their_earlier_one(self):
        at_head = [review("Concerns.", author="a"), review(CLEAN_BODY, author="a")]
        self.assertEqual(reviews_missing_marker(at_head, HEAD), [])

    def test_marker_for_a_different_commit_does_not_count(self):
        at_head = [review("Reviewed `deadbeef12` — no new issues found.")]
        self.assertEqual(len(reviews_missing_marker(at_head, HEAD)), 1)


class TestVerdict(unittest.TestCase):
    def test_clean_requires_an_explicit_all_clear_at_head(self):
        self.assertEqual(verdict_for(snapshot([review(CLEAN_BODY)]), [], HEAD, None), "clean")

    def test_unreviewed_pr_is_never_clean(self):
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None), "unreviewed")

    def test_review_of_an_older_commit_is_stale(self):
        self.assertEqual(verdict_for(snapshot([review(CLEAN_BODY, sha="old")]), [], HEAD, None), "stale")

    def test_reviewed_without_an_all_clear_is_unclear(self):
        self.assertEqual(verdict_for(snapshot([review("LGTM")]), [], HEAD, None), "unclear")

    def test_empty_review_body_is_unclear(self):
        self.assertEqual(verdict_for(snapshot([review("")]), [], HEAD, None), "unclear")

    def test_unresolved_thread_beats_a_clean_review(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(verdict_for(snap, [thread()], HEAD, None), "findings")

    def test_outdated_but_open_thread_still_counts_as_findings(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(verdict_for(snap, [thread(outdated=True)], HEAD, None), "findings")

    def test_changes_requested_without_threads_is_blocked_not_findings(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(verdict_for(snap, [], HEAD, "CHANGES_REQUESTED"), "blocked")

    def test_partial_fetch_never_reports_clean(self):
        snap = snapshot([review(CLEAN_BODY)], warning="reviewThreads query failed")
        self.assertEqual(verdict_for(snap, [], HEAD, None), "unknown")


class TestRequiredReview(unittest.TestCase):
    def test_missing_commissioned_review_is_never_clean(self):
        snap = snapshot([dict(review(CLEAN_BODY), id=111)])
        self.assertEqual(verdict_for(snap, [], HEAD, None, 999), "unreviewed")

    def test_present_commissioned_review_can_be_clean(self):
        snap = snapshot([dict(review(CLEAN_BODY), id=111)])
        self.assertEqual(verdict_for(snap, [], HEAD, None, 111), "clean")

    def test_id_parsed_from_review_url(self):
        url = "https://github.com/o/r/pull/39#pullrequestreview-4779445645"
        self.assertEqual(parse_review_id(url), 4779445645)

    def test_bare_id_and_empty(self):
        self.assertEqual(parse_review_id("123"), 123)
        self.assertIsNone(parse_review_id(None))


class TestResolveVerdict(unittest.TestCase):
    def pr(self, **over) -> dict:
        base = {"state": "OPEN", "isDraft": False, "reviewDecision": ""}
        base.update(over)
        return base

    def test_merged_pr_is_closed_even_when_clean(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(resolve_verdict(self.pr(state="MERGED"), snap, [], HEAD, False), "closed")

    def test_draft_pr_reports_draft(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(resolve_verdict(self.pr(isDraft=True), snap, [], HEAD, False), "draft")

    def test_timeout_beats_a_review_verdict(self):
        self.assertEqual(resolve_verdict(self.pr(), snapshot([]), [], HEAD, True), "timeout")

    def test_open_pr_falls_through_to_review_logic(self):
        snap = snapshot([review(CLEAN_BODY)])
        self.assertEqual(resolve_verdict(self.pr(), snap, [], HEAD, False), "clean")


class TestRequiredSignature(unittest.TestCase):
    SIG = "pr-review skill"
    SIGNED = f"{CLEAN_BODY}\n\n— {SIG} · Claude Opus 5"

    def test_signed_all_clear_is_clean(self):
        self.assertEqual(
            verdict_for(snapshot([review(self.SIGNED)]), [], HEAD, None, None, self.SIG),
            "clean",
        )

    def test_hand_typed_all_clear_without_signature_is_not_clean(self):
        self.assertEqual(
            verdict_for(snapshot([review(CLEAN_BODY)]), [], HEAD, None, None, self.SIG),
            "unclear",
        )

    def test_signature_not_required_by_default(self):
        self.assertEqual(verdict_for(snapshot([review(CLEAN_BODY)]), [], HEAD, None), "clean")

    def test_hidden_html_comment_satisfies_the_real_signature(self):
        body = NOTE + CLEAN_BODY + HIDDEN
        self.assertEqual(
            verdict_for(snapshot([review(body)]), [], HEAD, None, None, DEFAULT_SIGNATURE),
            "clean",
        )


def check_run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
    summary: str = "**Final Result:** Bugbot completed review - no issues found! ✅",
) -> dict:
    return {"id": 1, "name": "Cursor Bugbot", "app": "cursor", "status": status,
            "conclusion": conclusion, "summary": summary}


def attest(grade: str, *, sha: str | None = HEAD) -> dict:
    return {"kind": "check", "author": "cursor[bot]", "reviewer": "cursor-bugbot",
            "sha": sha.lower() if sha else None, "grade": grade}


class TestCheckRunGrading(unittest.TestCase):
    def test_success_is_clean(self):
        self.assertEqual(grade_check_run(check_run(), BUGBOT), "clean")

    def test_findings_round_is_unclear_so_the_threads_decide(self):
        run = check_run(conclusion="neutral",
                        summary="**Final Result:** Bugbot completed review and found 1 potential issue.")
        self.assertEqual(grade_check_run(run, BUGBOT), "unclear")

    def test_failed_run_is_failed_not_unclear(self):
        run = check_run(conclusion="neutral",
                        summary="✅ ❌ Bugbot run failed (9s)\n\n**Result:** Bugbot failed to run")
        self.assertEqual(grade_check_run(run, BUGBOT), "failed")

    def test_skipped_and_cancelled_never_reviewed(self):
        for conclusion in ("skipped", "cancelled", "timed_out"):
            with self.subTest(conclusion=conclusion):
                self.assertEqual(grade_check_run(check_run(conclusion=conclusion, summary=""), BUGBOT), "failed")

    def test_running_is_pending(self):
        run = check_run(status="in_progress", conclusion=None, summary="Bugbot Analysis Progress")
        self.assertEqual(grade_check_run(run, BUGBOT), "pending")

    def test_result_line_is_surfaced_without_markup(self):
        # "Posted analysis results" also contains the word; the "Result:" line
        # is the one that says what happened.
        summary = ("Bugbot Analysis Progress (2m 41s elapsed)\n\n✅ Gathered PR context (2s)\n"
                   "✅ Posted analysis results (1s)\n\n**Final Result:** Bugbot completed review"
                   " - no issues found! ✅\n\nRequest ID: x")
        self.assertEqual(check_result_line(summary), "Final Result: Bugbot completed review - no issues found! ✅")
        self.assertEqual(check_result_line("a\n\nlast line"), "last line")
        self.assertEqual(check_result_line(""), "")


class TestCheckAttestationVerdict(unittest.TestCase):
    def test_clean_check_alone_is_clean(self):
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None, attestations=[attest("clean")]), "clean")

    def test_clean_check_stays_clean_when_a_signature_is_required(self):
        # A check run cannot be typed by hand, so the signature rule that
        # guards the text channels does not apply to it.
        self.assertEqual(
            verdict_for(snapshot([]), [], HEAD, None, None, DEFAULT_SIGNATURE, [attest("clean")]),
            "clean",
        )

    def test_failed_run_reads_as_unreviewed(self):
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None, attestations=[attest("failed")]), "unreviewed")

    def test_pending_run_reads_as_unreviewed(self):
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None, attestations=[attest("pending")]), "unreviewed")

    def test_findings_round_with_open_threads_is_findings(self):
        self.assertEqual(verdict_for(snapshot([]), [thread()], HEAD, None, attestations=[attest("unclear")]), "findings")

    def test_findings_round_with_threads_resolved_is_unclear_not_clean(self):
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None, attestations=[attest("unclear")]), "unclear")

    def test_clean_check_does_not_outvote_a_review_without_the_marker(self):
        snap = snapshot([review("LGTM")])
        self.assertEqual(verdict_for(snap, [], HEAD, None, attestations=[attest("clean")]), "unclear")

    def bugbot_review(self, submitted_at: str) -> dict:
        return dict(
            review("Cursor Bugbot has reviewed your changes and found 1 potential issue.",
                   author="cursor[bot]"),
            submitted_at=submitted_at,
        )

    def later_check(self, completed_at: str) -> dict:
        return dict(attest("clean"), created_at=completed_at)

    def test_later_clean_check_supersedes_the_same_logins_findings_review(self):
        # Threads answered, Bugbot re-run on the same head, success: that is
        # Bugbot's latest word, and its earlier review must not hold the head.
        snap = snapshot([self.bugbot_review("2026-09-05T18:00:00Z")])
        self.assertEqual(
            verdict_for(snap, [], HEAD, None, attestations=[self.later_check("2026-09-05T18:26:58Z")]),
            "clean",
        )

    def test_no_new_issues_review_in_the_same_second_is_superseded(self):
        # Observed on a live PR: the "found no new issues" review and the
        # success check carry the same timestamp.
        snap = snapshot([dict(
            review("<!-- BUGBOT_REVIEW -->\n✅ Bugbot reviewed your changes and found no new issues!",
                   author="cursor[bot]"),
            submitted_at="2026-09-05T18:26:58Z",
        )])
        self.assertEqual(
            verdict_for(snap, [], HEAD, None, attestations=[self.later_check("2026-09-05T18:26:58Z")]),
            "clean",
        )

    def test_earlier_check_does_not_supersede_a_later_review(self):
        snap = snapshot([self.bugbot_review("2026-09-05T18:30:00Z")])
        self.assertEqual(
            verdict_for(snap, [], HEAD, None, attestations=[self.later_check("2026-09-05T18:26:58Z")]),
            "unclear",
        )

    def test_check_never_supersedes_another_logins_review(self):
        snap = snapshot([dict(review("Concerns.", author="human"), submitted_at="2026-09-05T18:00:00Z")])
        self.assertEqual(
            verdict_for(snap, [], HEAD, None, attestations=[self.later_check("2026-09-05T18:26:58Z")]),
            "unclear",
        )

    def test_open_threads_still_beat_a_superseding_check(self):
        snap = snapshot([self.bugbot_review("2026-09-05T18:00:00Z")])
        self.assertEqual(
            verdict_for(snap, [thread()], HEAD, None, attestations=[self.later_check("2026-09-05T18:26:58Z")]),
            "findings",
        )


class TestBugbotComments(unittest.TestCase):
    def comment(self, body: str) -> dict:
        return {"id": 1, "author": "cursor[bot]", "body": body, "url": "", "created_at": ""}

    def test_could_not_run_comment_is_failed(self):
        body = "<h3>Bugbot couldn't run - usage limit reached</h3>\n\nBugbot is counted against Cursor usage."
        attestation = comment_attestation(self.comment(body), HEAD, EXTERNAL_REVIEWER_PROFILES, None)
        self.assertEqual(attestation["grade"], "failed")
        self.assertEqual(
            verdict_for(snapshot([]), [], HEAD, None, attestations=[attestation]), "unreviewed"
        )

    def test_cursor_bot_prose_never_grades_clean(self):
        # The login is shared with Cursor's cloud agents, which post arbitrary
        # prose; only the check run may clear a head.
        body = f"Reviewed commit `{HEAD[:10]}` — no issues found, ready to merge."
        attestation = comment_attestation(self.comment(body), HEAD, EXTERNAL_REVIEWER_PROFILES, None)
        self.assertNotEqual(attestation["grade"], "clean")
        self.assertNotEqual(
            verdict_for(snapshot([]), [], HEAD, None, attestations=[attestation]), "clean"
        )


if __name__ == "__main__":
    unittest.main()
