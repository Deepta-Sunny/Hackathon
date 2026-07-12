import importlib.util
import sys
import types
from pathlib import Path


class _Prompt:
    def __init__(self, value: str):
        self.value = value


class _DatasetWithPrompts:
    def __init__(self, values):
        self.prompts = [_Prompt(v) for v in values]


def _load_pyrit_seed_loader_module(monkeypatch):
    pyrit_module = types.ModuleType("pyrit")
    datasets_module = types.ModuleType("pyrit.datasets")

    datasets_module.fetch_harmbench_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_many_shot_jailbreaking_dataset = lambda: []
    datasets_module.fetch_forbidden_questions_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_adv_bench_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_tdc23_redteaming_dataset = lambda: _DatasetWithPrompts([])

    monkeypatch.setitem(sys.modules, "pyrit", pyrit_module)
    monkeypatch.setitem(sys.modules, "pyrit.datasets", datasets_module)

    target = Path("/home/runner/work/Hackathon/Hackathon/BACKEND/utils/pyrit_seed_loader.py")
    spec = importlib.util.spec_from_file_location("pyrit_seed_loader_under_test", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_get_prompts_by_category_lazy_loads_only_required_datasets(monkeypatch):
    module = _load_pyrit_seed_loader_module(monkeypatch)
    loader = module.PyRITSeedLoader()

    called = []

    def _mark(name, payload):
        def _inner():
            called.append(name)
            return payload
        return _inner

    loader.DATASET_FETCHERS = {
        "harmbench": _mark("harmbench", _DatasetWithPrompts(["h1"])),
        "many_shot": _mark("many_shot", [{"user": "m1"}]),
        "forbidden": _mark("forbidden", _DatasetWithPrompts(["f1"])),
        "advbench": _mark("advbench", _DatasetWithPrompts(["a1"])),
        "tdc23": _mark("tdc23", _DatasetWithPrompts(["t1"])),
    }

    prompts = loader.get_prompts_by_category("obfuscation", count=10)

    assert set(called) == {"advbench", "many_shot"}
    assert set(loader._loaded_dataset_names) == {"advbench", "many_shot"}
    assert set(prompts) == {"a1", "m1"}


def test_get_prompts_by_category_unknown_category_returns_empty(monkeypatch):
    module = _load_pyrit_seed_loader_module(monkeypatch)
    loader = module.PyRITSeedLoader()

    called = []
    loader.DATASET_FETCHERS = {
        "harmbench": lambda: called.append("harmbench"),
    }

    prompts = loader.get_prompts_by_category("not_a_real_category", count=5)

    assert prompts == []
    assert called == []
    assert loader._loaded_dataset_names == set()


def test_crescendo_generator_uses_crescendo_category_reference_only():
    path = Path("/home/runner/work/Hackathon/Hackathon/BACKEND/core/crescendo_orchestrator.py")
    content = path.read_text(encoding="utf-8")

    assert 'pyrit_examples = self._get_pyrit_examples_context("crescendo")' in content
    assert 'examples = get_pyrit_examples_by_category(category, count=4)' in content
    assert 'get_pyrit_examples_by_category("jailbreak", count=2)' not in content
    assert 'get_pyrit_examples_by_category("harmful", count=2)' not in content
