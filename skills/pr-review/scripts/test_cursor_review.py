"""Tests for the paths that could turn a failed cursor review into a false clean."""

from __future__ import annotations

import json
import unittest

from cursor_review import (
    SIGNATURE,
    SIGNED_BY,
    agent_result,
    coerce_line,
    extract_object,
    normalise,
)


def envelope(result: str, *, is_error: bool = False) -> str:
    return json.dumps({"type": "result", "is_error": is_error, "result": result})


class TestAgentResult(unittest.TestCase):
    def test_reads_the_result_field(self):
        self.assertEqual(agent_result(envelope("hello")), "hello")

    def test_error_envelope_is_fatal(self):
        with self.assertRaises(SystemExit) as caught:
            agent_result(envelope("rate limited", is_error=True))
        self.assertEqual(caught.exception.code, 1)

    def test_bare_error_line_is_not_parsed_as_a_review(self):
        # An unusable model string prints this instead of an envelope.
        for text in ("Error: [internal]", "Cannot use this model: claude-x[bogus=1]"):
            with self.assertRaises(SystemExit):
                agent_result(text)

    def test_empty_output_is_fatal(self):
        for text in ("", "   ", envelope("")):
            with self.assertRaises(SystemExit):
                agent_result(text)


class TestExtractObject(unittest.TestCase):
    def test_plain_fenced_block(self):
        reply = '```json\n{"findings": [], "suspicions": []}\n```'
        self.assertEqual(extract_object(reply), {"findings": [], "suspicions": []})

    def test_unfenced_object(self):
        self.assertEqual(extract_object('{"findings": []}'), {"findings": []})

    def test_takes_the_last_block_when_the_schema_is_restated_first(self):
        reply = (
            "Here is the shape I will use:\n"
            '```json\n{"findings": [{"path": "example.ts"}]}\n```\n'
            "And here is the review:\n"
            '```json\n{"findings": [], "suspicions": []}\n```\n'
        )
        self.assertEqual(extract_object(reply)["findings"], [])

    def test_prose_around_the_block_is_tolerated(self):
        reply = 'I reviewed it.\n\n```json\n{"findings": [], "suspicions": []}\n```\n\nDone.'
        self.assertEqual(extract_object(reply), {"findings": [], "suspicions": []})

    def test_no_object_at_all_is_fatal(self):
        # The failure that matters: a chatty non-answer must not read as "no findings".
        for reply in ("I could not access the diff.", "```json\nnot json\n```", "[]"):
            with self.assertRaises(SystemExit):
                extract_object(reply)


class TestNormalise(unittest.TestCase):
    def finding(self, **over) -> dict:
        base = {"path": "src/a.ts", "line": 12, "side": "RIGHT", "severity": "P1",
                "title": "Fix it", "body": "Because."}
        base.update(over)
        return base

    def test_empty_review_is_a_valid_result(self):
        self.assertEqual(normalise({"findings": [], "suspicions": []}), ([], []))

    def test_missing_arrays_default_to_empty(self):
        self.assertEqual(normalise({}), ([], []))

    def test_error_key_exits_three(self):
        with self.assertRaises(SystemExit) as caught:
            normalise({"error": "the diff was truncated"})
        self.assertEqual(caught.exception.code, 3)

    def test_error_key_wins_over_an_empty_findings_array(self):
        with self.assertRaises(SystemExit) as caught:
            normalise({"error": "ran out of context", "findings": []})
        self.assertEqual(caught.exception.code, 3)

    def test_lowercase_side_is_uppercased(self):
        # pr_review.py matches anchors by exact case; "right" matches no hunk
        # and fails the whole atomic POST.
        findings, _ = normalise({"findings": [self.finding(side="right")]})
        self.assertEqual(findings[0]["side"], "RIGHT")

    def test_lowercase_severity_is_uppercased(self):
        findings, _ = normalise({"findings": [self.finding(severity="p2")]})
        self.assertEqual(findings[0]["severity"], "P2")

    def test_unknown_severity_is_fatal(self):
        for sev in ("P0", "critical", "", None):
            with self.assertRaises(SystemExit):
                normalise({"findings": [self.finding(severity=sev)]})

    def test_unknown_side_is_fatal(self):
        with self.assertRaises(SystemExit):
            normalise({"findings": [self.finding(side="middle")]})

    def test_absent_side_is_left_alone(self):
        f = self.finding()
        del f["side"]
        findings, _ = normalise({"findings": [f]})
        self.assertNotIn("side", findings[0])

    def test_string_line_is_coerced(self):
        findings, _ = normalise({"findings": [self.finding(line="84")]})
        self.assertEqual(findings[0]["line"], 84)

    def test_non_integer_line_is_fatal(self):
        with self.assertRaises(SystemExit):
            normalise({"findings": [self.finding(line="somewhere near the top")]})

    def test_null_suspicion_line_becomes_a_file_level_anchor(self):
        _, suspicions = normalise({"suspicions": [
            {"path": "src/a.ts", "line": None, "consequence": "c", "check": "k"}
        ]})
        self.assertNotIn("line", suspicions[0])

    def test_non_list_findings_is_fatal(self):
        with self.assertRaises(SystemExit):
            normalise({"findings": {"path": "src/a.ts"}})

    def test_non_object_finding_is_fatal(self):
        with self.assertRaises(SystemExit):
            normalise({"findings": ["src/a.ts:12 is wrong"]})


class TestCoerceLine(unittest.TestCase):
    def test_booleans_are_not_lines(self):
        # True is an int in Python and would otherwise anchor at line 1.
        self.assertIsNone(coerce_line(True))
        self.assertIsNone(coerce_line(False))

    def test_accepts_ints_and_digit_strings(self):
        self.assertEqual(coerce_line(7), 7)
        self.assertEqual(coerce_line(" 7 "), 7)

    def test_rejects_the_rest(self):
        for value in (None, 1.5, "top", "", [], {}):
            self.assertIsNone(coerce_line(value))


class TestSignature(unittest.TestCase):
    def test_signature_carries_the_string_pr_watch_requires(self):
        # pr_watch.py refuses a clean verdict unless the review body contains
        # this substring, so a cursor review that signed only as itself would
        # never converge.
        self.assertIn(SIGNATURE, SIGNED_BY)

    def test_signature_names_the_agent_and_model(self):
        self.assertIn("cursor-agent", SIGNED_BY)
        self.assertIn("claude-opus-4-6", SIGNED_BY)


if __name__ == "__main__":
    unittest.main()
