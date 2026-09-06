"""Tests for the verdict logic — the one function that can emit a false clean."""

from __future__ import annotations

import unittest
from unittest import mock

from pr_watch import (
    DEFAULT_SIGNATURE,
    EXTERNAL_REVIEWER_PROFILES,
    clean_marker_sha,
    comment_attestation,
    parse_review_id,
    reaction_attestation,
    resolve_verdict,
    reviews_missing_marker,
    verdict_for,
)

HEAD = "9272601754ee1b5c6209649b4753b76680d91d83"
CLEAN_BODY = f"Reviewed `{HEAD[:10]}` — no new issues found."
# What pr_review.py post renders around the verdict line.
NOTE = "> [!NOTE]\n> 🤖 Reviewed by Claude/Opus-5\n\n"
HIDDEN = f"\n\n<!-- {DEFAULT_SIGNATURE} -->"


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


CODEX = "chatgpt-codex-connector[bot]"
TRIGGER = {"id": 7, "url": "", "created_at": "2026-09-05T18:00:00Z"}


def thumbs_up(author: str) -> dict:
    return {"author": author, "content": "+1", "created_at": "2026-09-05T18:01:00Z"}


def reaction(reactions: list[dict]) -> dict | None:
    # The trigger comment postdates the head commit, so a +1 on it is anchored.
    with mock.patch("pr_watch.fetch_reactions", return_value=reactions), \
         mock.patch("pr_watch.head_committed_at", return_value="2026-09-05T17:00:00Z"):
        return reaction_attestation("o/r", HEAD, TRIGGER, EXTERNAL_REVIEWER_PROFILES, None)


class TestUnknownBots(unittest.TestCase):
    """A bot the watcher has no profile for — one installed on the repository
    and running on its own — wakes the wait but can never clear the head."""

    def test_all_clear_prose_from_an_unknown_bot_never_grades_clean(self):
        comment = {"id": 1, "author": "somebot[bot]", "url": "", "created_at": "",
                   "body": f"Reviewed commit `{HEAD[:10]}` — no issues found, ready to merge."}
        attestation = comment_attestation(comment, HEAD, EXTERNAL_REVIEWER_PROFILES, None)
        self.assertEqual(attestation["grade"], "unclear")
        self.assertNotEqual(
            verdict_for(snapshot([]), [], HEAD, None, attestations=[attestation]), "clean"
        )

    def test_thumbs_up_from_an_unknown_bot_grades_unclear(self):
        attestation = reaction([thumbs_up("somebot[bot]")])
        self.assertEqual(attestation["grade"], "unclear")
        self.assertEqual(
            verdict_for(snapshot([]), [], HEAD, None, attestations=[attestation]), "unclear"
        )

    def test_codex_thumbs_up_still_grades_clean(self):
        attestation = reaction([thumbs_up(CODEX)])
        self.assertEqual(attestation["grade"], "clean")
        self.assertEqual(verdict_for(snapshot([]), [], HEAD, None, attestations=[attestation]), "clean")

    def test_codex_thumbs_up_outranks_a_stray_bots(self):
        attestation = reaction([thumbs_up("somebot[bot]"), thumbs_up(CODEX)])
        self.assertEqual((attestation["author"], attestation["grade"]), (CODEX, "clean"))


if __name__ == "__main__":
    unittest.main()
