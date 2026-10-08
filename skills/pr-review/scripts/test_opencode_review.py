"""Tests for the paths that could turn a failed opencode review into a false clean."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from opencode_review import (
    DEFAULT_MODEL,
    READ_ONLY_BASH,
    SHELL_NOTE,
    agent_result,
    event_error,
    permission_config,
    reviewer_label,
)


def text(message: str, body: str) -> str:
    return json.dumps({"type": "text", "part": {"messageID": message, "type": "text", "text": body}})


def step_finish(message: str, reason: str = "stop") -> str:
    return json.dumps({"type": "step_finish", "part": {"messageID": message, "reason": reason}})


def error(message: str) -> str:
    return json.dumps({"type": "error", "error": {"type": "provider.no-route", "message": message}})


class TestAgentResult(unittest.TestCase):
    def test_reads_the_last_message_only(self):
        # Narration before a tool call is an earlier message, not the review.
        stream = "\n".join([
            text("m1", "Checking the diff first."),
            step_finish("m1", "tool-calls"),
            text("m2", '```json\n{"findings": []}\n```'),
            step_finish("m2"),
        ])
        self.assertEqual(agent_result(stream), '```json\n{"findings": []}\n```')

    def test_joins_text_parts_of_the_last_message(self):
        stream = "\n".join([text("m2", "```json\n"), text("m2", '{"findings": []}\n```')])
        self.assertEqual(agent_result(stream), '```json\n{"findings": []}\n```')

    def test_error_event_is_fatal(self):
        with self.assertRaises(SystemExit) as caught:
            agent_result(error("Model unavailable: opencode/x"))
        self.assertEqual(caught.exception.code, 1)

    def test_error_event_wins_over_text(self):
        stream = "\n".join([text("m1", '{"findings": []}'), error("rate limited")])
        with self.assertRaises(SystemExit):
            agent_result(stream)

    def test_bare_line_is_not_parsed_as_a_review(self):
        with self.assertRaises(SystemExit):
            agent_result("Error: not logged in")

    def test_empty_output_is_fatal(self):
        for stdout in ("", "   ", step_finish("m1"), text("m1", "  ")):
            with self.subTest(stdout=stdout), self.assertRaises(SystemExit):
                agent_result(stdout)

    def test_event_error_reads_the_message(self):
        self.assertEqual(event_error(error("Model unavailable")), "Model unavailable")
        self.assertIsNone(event_error(text("m1", "hi")))


class TestPermissions(unittest.TestCase):
    def test_edits_and_web_are_denied(self):
        perms = permission_config(Path("/tmp/work"))["permission"]
        for key in ("edit", "webfetch", "websearch"):
            self.assertEqual(perms[key], "deny")

    def test_only_the_workdir_is_reachable_outside_the_workspace(self):
        external = permission_config(Path("/tmp/work"))["permission"]["external_directory"]
        self.assertEqual(external, {"*": "deny", "/tmp/work/*": "allow"})

    def test_shell_defaults_to_deny_not_ask(self):
        # "ask" would hang a non-interactive run waiting for approval.
        self.assertEqual(next(iter(READ_ONLY_BASH.items())), ("*", "deny"))
        self.assertNotIn("ask", READ_ONLY_BASH.values())

    def test_write_forms_are_denied_after_the_reads_they_override(self):
        # Last match wins, so each denial must come after the allowance it narrows.
        keys = list(READ_ONLY_BASH)
        last_allow = max(i for i, k in enumerate(keys) if READ_ONLY_BASH[k] == "allow")
        for pattern in ("*>*", "*--output*", "gh api * -X*", "gh api * -f *", "gh api * --input*"):
            with self.subTest(pattern=pattern):
                self.assertEqual(READ_ONLY_BASH[pattern], "deny")
                self.assertGreater(keys.index(pattern), last_allow)


    def test_the_quoted_gh_api_read_from_the_method_is_allowed(self):
        # The method prints `gh api "repos/..."`; denying it leaves the agent
        # reviewing a diff without the code around it.
        self.assertEqual(READ_ONLY_BASH['gh api "repos/*'], "allow")

    def test_the_prompt_turns_an_unreadable_codebase_into_an_error(self):
        self.assertIn('{"error":', SHELL_NOTE)
        self.assertIn("Never return an empty review", SHELL_NOTE)


class TestReviewerLabel(unittest.TestCase):
    def test_default_model_is_muse_spark_free_on_zen(self):
        self.assertEqual(DEFAULT_MODEL, "opencode/muse-spark-1.3-contributor-free")

    def test_default_label_drops_provider_and_tier(self):
        self.assertEqual(reviewer_label(DEFAULT_MODEL), "OpenCode/Muse-Spark-1.3-Contributor")

    def test_label_follows_a_model_override(self):
        self.assertEqual(reviewer_label("opencode/big-pickle"), "OpenCode/Big-Pickle")
        self.assertEqual(reviewer_label("anthropic/claude-opus-5"), "OpenCode/Opus-5")


if __name__ == "__main__":
    unittest.main()
