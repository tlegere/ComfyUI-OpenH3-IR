"""Prompt Only uses the author's Main panel without duplicating its input UI."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN = (ROOT / "web" / "main.js").read_text(encoding="utf-8")
PICKER = (ROOT / "web" / "prompt.js").read_text(encoding="utf-8")
NODES = (ROOT / "nodes.py").read_text(encoding="utf-8")


def test_main_panel_is_attached_to_both_node_types():
    assert 'const NODES = ["OpenH3IRCompile", "OpenH3IRPromptOnly"];' in MAIN
    assert "if (!NODES.includes(nodeData?.name)) return;" in MAIN
    assert 'textContent: promptOnly ? "Prompt Only" : "Main"' in MAIN
    assert 'promptOnly ? "compile without H3 model loading"' in MAIN


def test_prompt_only_reuses_the_same_widgets_and_mention_editor():
    assert "inputs=main.inputs" in NODES
    assert "const panel = new Panel(this, by, promptOnly);" in MAIN
    assert "attachPrompt(panel.box, this)" in MAIN
    assert 'const NODES = ["OpenH3IRCompile", "OpenH3IRPromptOnly"];' in PICKER
    assert "if (!NODES.includes(nodeData?.name)) return;" in PICKER
    assert "this._oh3Chips?.check();" in PICKER


def test_prompt_only_reserves_less_space_for_its_two_output_sockets():
    assert "const NODE_H_EXTRA = 178;" in MAIN
    assert "const PROMPT_ONLY_NODE_H_EXTRA = 98;" in MAIN
    assert "const PROMPT_ONLY_NODE_H = NODE_H -" in MAIN
    assert "const PROMPT_ONLY_MIN_H = MIN_H -" in MAIN
    assert "const socketHeight = promptOnly ? PROMPT_ONLY_NODE_H_EXTRA : NODE_H_EXTRA;" in MAIN
    assert "Math.max(minHeight, this.size?.[1] || height) - socketHeight" in MAIN


def test_existing_main_node_identifiers_and_geometry_remain_unchanged():
    for entry in ("const NODE_W = 520;", "const NODE_H = 773;",
                  "const MIN_W = 430;", "const MIN_H = 719;",
                  'const BOARD = "oh3m_panel";',
                  "this._oh3Main = panel;"):
        assert entry in MAIN
