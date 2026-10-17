"""Diagnostics must explain validation fallbacks without changing the accepted prompt."""
from __future__ import annotations

from types import SimpleNamespace

from openh3ir.compiler import compilation_diagnostics


def _doc(*, source="written", fallback_reason=None, provenance=None, findings=None):
    return SimpleNamespace(
        fell_back=source == "draft" and bool(fallback_reason),
        source=source, fallback_reason=fallback_reason,
        provenance=provenance or {}, findings=findings or [],
    )


def test_accepted_first_pass_is_reported_without_inventing_rejected_text():
    d = compilation_diagnostics(_doc(
        provenance={"fix_rounds": 0, "timings": {"compose_s": 4.2}}))
    assert d["available"] is True
    assert d["status"] == "written"
    assert d["correction_rounds"] == 0
    assert d["last_rejected_brief"] is None
    assert d["timings_seconds"]["compose_s"] == 4.2
    assert "initial and intermediate" in d["trace_limitations"]


def test_fallback_preserves_the_last_rejected_written_brief_and_real_errors():
    rule = "T12-cut-inside-the-floor"
    rejected = "integrated_multimodal_description: [Shot 1] A great, but invalid, take"
    d = compilation_diagnostics(_doc(
        source="draft", fallback_reason="the written brief still failed",
        provenance={"rejected_written": rejected, "fix_rounds": 2,
                    "rejected_rules": [rule + ": shot 5 too short"],
                    "repairs": ["fixed text header"],
                    "unfixable": [rule],
                    "timings": {"fix1_s": 6.1, "fix2_s": 6.2}},
        findings=[SimpleNamespace(severity="WARN", rule="X13-written-rejected",
                                  msg="failed")]))
    assert d["status"] == "fallback"
    assert d["correction_rounds"] == 2
    assert d["last_rejected_brief"] == rejected
    assert d["remaining_validation_errors"][0].startswith(rule)
    assert d["persisting_rules"] == [rule]
    assert d["findings"][0]["rule"] == "X13-written-rejected"


def test_model_error_fallback_has_unknown_correction_count_and_no_candidate():
    d = compilation_diagnostics(_doc(
        source="draft", fallback_reason="TruncatedResponse: hit max_tokens (20000)"))
    assert d["status"] == "fallback"
    assert d["correction_rounds"] is None
    assert d["last_rejected_brief"] is None
    assert not d["remaining_validation_errors"]


def test_trace_has_no_effect_on_the_original_prompt_report_schema():
    # Diagnostics only enter the in-process reply when include_diagnostics=True.
    # The normal Main and remote-service paths retain their previous output shape.
    import inspect
    from openh3ir.compiler import compile_here
    assert inspect.signature(compile_here).parameters["include_diagnostics"].default is False
