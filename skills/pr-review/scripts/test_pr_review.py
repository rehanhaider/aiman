#!/usr/bin/env python3
"""Unit tests for pr_review.py's pure logic — run with:  python3 scripts/test_pr_review.py"""

import unittest

from pr_review import (
    PR_URL_RE,
    commentable_lines,
    drop_low_priority,
    finding_to_comment,
    render_comment_body,
    render_summary,
    split_findings,
    url_matches,
    validate_comments,
    validate_findings,
)

# One modified file (context, delete, adds, blank context line with stripped
# trailing space), one deleted file (with no-newline marker), one new file.
DIFF = "\n".join([
    "diff --git a/src/app.py b/src/app.py",
    "index 1111111..2222222 100644",
    "--- a/src/app.py",
    "+++ b/src/app.py",
    "@@ -1,4 +1,5 @@",
    " import os",
    "-import sys",
    "+import sys, json",
    "+import re",
    "",
    " def main():",
    "diff --git a/gone.txt b/gone.txt",
    "deleted file mode 100644",
    "--- a/gone.txt",
    "+++ /dev/null",
    "@@ -1,2 +0,0 @@",
    "-a",
    "-b",
    "\\ No newline at end of file",
    "diff --git a/new.txt b/new.txt",
    "new file mode 100644",
    "--- /dev/null",
    "+++ b/new.txt",
    "@@ -0,0 +1,2 @@",
    "+x",
    "+y",
])


class TestCommentableLines(unittest.TestCase):
    def setUp(self):
        self.files = commentable_lines(DIFF)

    def test_modified_file_right_and_left(self):
        self.assertEqual(self.files["src/app.py"]["RIGHT"], {1, 2, 3, 4, 5})
        self.assertEqual(self.files["src/app.py"]["LEFT"], {1, 2, 3, 4})

    def test_deleted_file_keeps_old_path_left_only(self):
        self.assertEqual(self.files["gone.txt"]["LEFT"], {1, 2})
        self.assertEqual(self.files["gone.txt"]["RIGHT"], set())

    def test_new_file_right_only(self):
        self.assertEqual(self.files["new.txt"]["RIGHT"], {1, 2})
        self.assertEqual(self.files["new.txt"]["LEFT"], set())


class TestValidateComments(unittest.TestCase):
    def test_valid_anchors_pass(self):
        comments = [
            {"path": "src/app.py", "line": 3, "body": "x"},
            {"path": "src/app.py", "line": 2, "side": "LEFT", "body": "x"},
            {"path": "gone.txt", "line": 2, "side": "LEFT", "body": "x"},
            {"path": "src/app.py", "line": 5, "start_line": 2, "body": "x"},
            {"path": "src/app.py", "body": "file-level"},
        ]
        self.assertEqual(validate_comments(comments, DIFF), [])

    def test_miss_reports_nearest_line(self):
        errors = validate_comments([{"path": "src/app.py", "line": 42, "body": "x"}], DIFF)
        self.assertEqual(len(errors), 1)
        self.assertIn("nearest commentable RIGHT line is 5", errors[0])

    def test_unknown_file(self):
        errors = validate_comments([{"path": "nope.py", "line": 1, "body": "x"}], DIFF)
        self.assertIn("not in the PR diff", errors[0])

    def test_side_with_no_commentable_lines(self):
        errors = validate_comments([{"path": "new.txt", "line": 1, "side": "LEFT", "body": "x"}], DIFF)
        self.assertIn("no commentable LEFT lines", errors[0])

    def test_bad_start_line(self):
        errors = validate_comments(
            [{"path": "src/app.py", "line": 5, "start_line": 99, "body": "x"}], DIFF
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("src/app.py:99", errors[0])

    def test_missing_body(self):
        errors = validate_comments([{"path": "src/app.py", "line": 3}], DIFF)
        self.assertIn("missing required", errors[0])


class TestFindings(unittest.TestCase):
    def test_schema_validation(self):
        self.assertEqual(validate_findings([]), [])
        self.assertTrue(validate_findings({"not": "a list"}))
        errs = validate_findings([{"path": "a", "severity": "P9", "title": "t", "body": "b"}])
        self.assertTrue(any("severity" in e for e in errs))
        errs = validate_findings([{"path": "a", "severity": "P1", "body": "b"}])
        self.assertTrue(any("'title'" in e for e in errs))
        errs = validate_findings([{"path": "a", "severity": "P1", "title": "t", "body": "b", "line": "3"}])
        self.assertTrue(any("integer" in e for e in errs))
        errs = validate_findings(
            [{"path": "a", "severity": "P1", "title": "t", "body": "b", "line": 3, "start_line": 7}]
        )
        self.assertTrue(any("less than" in e for e in errs))
        errs = validate_findings(
            [{"path": "a", "severity": "P1", "title": "t" * 121, "body": "b"}]
        )
        self.assertTrue(any("120 characters" in e for e in errs))
        errs = validate_findings(
            [{"path": "a", "severity": "P1", "title": "t", "body": "word " * 121}]
        )
        self.assertTrue(any("120 words" in e for e in errs))

    def test_split_sorts_by_severity_stable(self):
        findings = [
            {"path": "a", "severity": "P3", "title": "a", "body": "."},
            {"path": "b", "severity": "P1", "title": "b", "body": "."},
            {"path": "c", "severity": "P3", "title": "c", "body": "."},
            {"path": "d", "severity": "P2", "title": "d", "body": "."},
        ]
        inline, folded = split_findings(findings, 2)
        self.assertEqual([f["title"] for f in inline], ["b", "d"])
        self.assertEqual([f["title"] for f in folded], ["a", "c"])

    def test_split_never_folds_p1_or_p2(self):
        findings = [
            {"path": "a", "severity": "P1", "title": "a", "body": "."},
            {"path": "b", "severity": "P2", "title": "b", "body": "."},
            {"path": "c", "severity": "P2", "title": "c", "body": "."},
            {"path": "d", "severity": "P3", "title": "d", "body": "."},
        ]
        inline, folded = split_findings(findings, 1)
        self.assertEqual([f["title"] for f in inline], ["a", "b", "c"])
        self.assertEqual([f["title"] for f in folded], ["d"])

    def test_drop_low_priority_partitions_in_order(self):
        findings = [
            {"path": "a", "severity": "P3", "title": "a", "body": "."},
            {"path": "b", "severity": "P1", "title": "b", "body": "."},
            {"path": "c", "severity": "P4", "title": "c", "body": "."},
            {"path": "d", "severity": "P2", "title": "d", "body": "."},
        ]
        posted, low = drop_low_priority(findings)
        self.assertEqual([f["title"] for f in posted], ["b", "d"])
        self.assertEqual([f["title"] for f in low], ["a", "c"])

    def test_only_low_findings_render_the_all_clear(self):
        # A review whose only survivors are P3/P4 posts the all-clear sentence:
        # the automated loop must read it as ready to merge, not as unreviewed.
        findings = [
            {"path": "a", "severity": "P3", "title": "a", "body": "."},
            {"path": "b", "severity": "P4", "title": "b", "body": "."},
        ]
        posted, low = drop_low_priority(findings)
        self.assertEqual(posted, [])
        self.assertEqual(len(low), 2)
        body = render_summary("abcdef12345", posted, [])
        self.assertIn("no new issues found", body)
        self.assertNotIn("P3", body)
        self.assertNotIn("P4", body)


class TestRendering(unittest.TestCase):
    def test_badge_markup_and_colors(self):
        for sev, color in (("P1", "orange"), ("P2", "yellow"), ("P3", "lightgrey"), ("P4", "lightgrey")):
            body = render_comment_body({"severity": sev, "title": "Fix it", "body": "Because."})
            self.assertTrue(body.startswith(
                f"**<sub><sub>![{sev} Badge](https://img.shields.io/badge/{sev}-{color}?style=flat)</sub></sub>  Fix it**"
            ))
            self.assertIn("\n\nBecause.", body)
            self.assertNotIn("👍", body)

    def test_comment_defaults_and_passthrough(self):
        c = finding_to_comment({"path": "a.py", "line": 9, "severity": "P2", "title": "t", "body": "b"})
        self.assertEqual((c["line"], c["side"]), (9, "RIGHT"))
        c = finding_to_comment({"path": "a.py", "line": 9, "start_line": 5, "side": "LEFT",
                                "severity": "P2", "title": "t", "body": "b"})
        self.assertEqual((c["start_line"], c["start_side"]), (5, "LEFT"))
        c = finding_to_comment({"path": "a.py", "severity": "P2", "title": "t", "body": "b"})
        self.assertNotIn("line", c)
        self.assertNotIn("side", c)

    def test_summary_counts_and_commit(self):
        findings = [
            {"path": "a", "line": 1, "severity": "P1", "title": "one", "body": "."},
            {"path": "b", "line": 2, "severity": "P3", "title": "two", "body": "."},
            {"path": "c", "line": 3, "severity": "P3", "title": "three", "body": "."},
        ]
        body = render_summary("31ded9d53a0123456789", findings, [], None)
        self.assertEqual(
            body,
            "Reviewed `31ded9d53a` — 3 findings (1 P1, 2 P3).\n",
        )
        self.assertNotIn("Additional findings", body)

    def test_summary_zero_findings(self):
        body = render_summary("abc1234567", [], [], None)
        self.assertEqual(body, "Reviewed `abc1234567` — no new issues found.\n")

    def test_signature_is_a_trailer_not_the_first_line(self):
        body = render_summary("abc1234567", [], [], "pr-review skill · Claude Opus 5")
        first, *_ = body.splitlines()
        self.assertEqual(first, "Reviewed `abc1234567` — no new issues found.")
        self.assertTrue(body.rstrip().endswith("— pr-review skill · Claude Opus 5"))

    def test_empty_signature_adds_nothing(self):
        self.assertEqual(
            render_summary("abc1234567", [], [], ""),
            "Reviewed `abc1234567` — no new issues found.\n",
        )

    def test_summary_folds_only_finding_titles(self):
        folded = [{"path": "x.py", "line": 7, "severity": "P4", "title": "Tidy the thing", "body": "."}]
        body = render_summary("abc1234567", folded, folded, None)
        self.assertIn("Additional low-priority findings:", body)
        self.assertIn("- **P4** `x.py:7` — Tidy the thing", body)


class TestTargetParsing(unittest.TestCase):
    def test_pr_url_variants(self):
        for url in (
            "https://github.com/owner/repo/pull/12",
            "https://github.com/owner/repo/pull/12/files#r123",
            "https://www.github.com/owner/repo/pull/12",
        ):
            m = PR_URL_RE.search(url)
            self.assertIsNotNone(m, url)
            self.assertEqual((m.group(1), m.group(2), m.group(3)), ("owner", "repo", "12"))
        self.assertIsNone(PR_URL_RE.search("https://github.com/owner/repo/issues/12"))

    def test_remote_url_matching(self):
        self.assertTrue(url_matches("git@github.com:Owner/Repo.git", "owner/repo"))
        self.assertTrue(url_matches("https://github.com/owner/repo", "owner/repo"))
        self.assertFalse(url_matches("git@github.com:owner/other.git", "owner/repo"))
        self.assertFalse(url_matches("https://github.com/prefix-owner/repo", "owner/repo"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
