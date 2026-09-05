"""Tests for the paths that could turn a failed cursor review into a false clean."""

from __future__ import annotations

import json
import unittest

from cursor_review import (
    DEFAULT_MODEL,
    agent_result,
    coerce_line,
    extract_object,
    normalise,
    pretty_model,
    reviewer_label,
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


class TestReviewerLabel(unittest.TestCase):
    def test_default_model_reads_as_harness_slash_model(self):
        self.assertEqual(reviewer_label(DEFAULT_MODEL), "Cursor/Opus-5")

    def test_default_model_pins_the_300k_window(self):
        # The plain `claude-opus-5-thinking-xhigh` id is the 1M variant; the
        # window is only selectable through the bracket parameters.
        self.assertIn("context=300k", DEFAULT_MODEL)
        self.assertIn("effort=xhigh", DEFAULT_MODEL)

    def test_label_follows_a_model_override(self):
        # The label must come from the model that ran, not from a constant:
        # a review by another model signed as Opus would be a false record.
        self.assertEqual(reviewer_label("grok-4-7"), "Cursor/Grok-4.7")
        self.assertEqual(reviewer_label("gpt-5.1-codex[effort=high]"), "Cursor/GPT-5.1-Codex")

    def test_bracket_parameters_never_reach_the_label(self):
        self.assertNotIn("[", reviewer_label(DEFAULT_MODEL))
        self.assertNotIn("thinking", reviewer_label(DEFAULT_MODEL))

    def test_pretty_model_examples(self):
        for raw, pretty in (
            ("claude-opus-5", "Opus-5"),
            ("claude-sonnet-4-5", "Sonnet-4.5"),
            ("gemini-2.5-pro", "Gemini-2.5-Pro"),
            ("composer-1", "Composer-1"),
            ("grok-4.7", "Grok-4.7"),
            # Real ids from `cursor-agent --list-models`.
            ("gpt-5.6-sol-xhigh", "GPT-5.6-Sol"),
            ("gpt-5.3-codex-xhigh-fast", "GPT-5.3-Codex"),
            ("cursor-grok-4.6-xhigh", "Grok-4.6"),
            ("claude-opus-5-thinking-max-fast", "Opus-5"),
            ("gemini-3.7-flash-high", "Gemini-3.7-Flash"),
            ("composer-2.5-fast", "Composer-2.5"),
            ("gpt-5.5-extra-high-fast", "GPT-5.5"),
            ("gemini-3.6-flash-minimal", "Gemini-3.6-Flash"),
            ("gpt-5.6-terra-none", "GPT-5.6-Terra"),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(pretty_model(raw), pretty)

    def test_unreadable_id_passes_through(self):
        self.assertEqual(pretty_model("  "), "")
        self.assertEqual(pretty_model("x"), "X")


if __name__ == "__main__":
    unittest.main()
