from __future__ import annotations

import ast
import builtins
from pathlib import Path

import pytest

import models
from plugins._kokoro_tts.helpers import runtime as kokoro_runtime
from plugins._whisper_stt.helpers import runtime as whisper_runtime


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _block_import(monkeypatch: pytest.MonkeyPatch, blocked_module: str) -> None:
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == blocked_module:
            raise ImportError(f"blocked import: {blocked_module}")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)


def test_models_require_local_embeddings_extra_only_when_used(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_import(monkeypatch, "sentence_transformers")

    with pytest.raises(ImportError, match="requirements.local-embeddings.txt"):
        models._load_sentence_transformer()


def test_whisper_runtime_reports_missing_voice_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_import(monkeypatch, "whisper")

    with pytest.raises(RuntimeError, match="requirements.voice.txt"):
        whisper_runtime._load_whisper_module()


def test_kokoro_runtime_reports_missing_voice_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_import(monkeypatch, "soundfile")

    with pytest.raises(RuntimeError, match="requirements.voice.txt"):
        kokoro_runtime._load_soundfile()


def test_lite_modules_no_longer_import_optional_dependencies_at_module_load() -> None:
    models_source = (PROJECT_ROOT / "models.py").read_text(encoding="utf-8")
    preload_source = (PROJECT_ROOT / "preload.py").read_text(encoding="utf-8")
    whisper_source = (
        PROJECT_ROOT / "plugins/_whisper_stt/helpers/runtime.py"
    ).read_text(encoding="utf-8")
    kokoro_source = (
        PROJECT_ROOT / "plugins/_kokoro_tts/helpers/runtime.py"
    ).read_text(encoding="utf-8")

    def imported_modules(source: str) -> set[str]:
        parsed = ast.parse(source)
        modules: set[str] = set()
        for node in parsed.body:
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        return modules

    assert "sentence_transformers" not in imported_modules(models_source)
    assert "plugins._whisper_stt.helpers" not in imported_modules(preload_source)
    assert "plugins._kokoro_tts.helpers" not in imported_modules(preload_source)
    assert "whisper" not in imported_modules(whisper_source)
    assert "soundfile" not in imported_modules(kokoro_source)
