# -*- coding: utf-8 -*-
"""Context tests."""

import json
from pathlib import Path

import pytest


def test_get_context(context_handler):
    """Get the context content."""
    assert context_handler is not None


def test_get_context_file(context_handler):
    """Get the context file path, validate it."""
    assert Path(context_handler.get_context_file()).exists()


def test_set_context_file(context_handler, tmp_path):
    """Set the new context file path, get it and validate."""
    new_path = Path(tmp_path).joinpath("new_context")
    context_handler.set_context_file(str(new_path))
    assert context_handler.get_context_file() == str(new_path)


def test_load_context_failed(context_handler, monkeypatch):
    """Attempt to load the context failed."""
    monkeypatch.setattr(json, "loads", Exception("Exception"))
    with pytest.raises(Exception):
        context_handler.load_context()
