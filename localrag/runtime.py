"""Foundry Local startup, execution providers, model download and loading."""
import sys

from . import config

from foundry_local_sdk import Configuration, FoundryLocalManager


def _bar(label: str, percent: float, width: int = 28) -> None:
    filled = int(width * percent / 100)
    line = f"\r  {label:<22} [{'#' * filled}{'.' * (width - filled)}] {percent:5.1f}%"
    sys.stdout.write(line)
    sys.stdout.flush()


def start(app_name: str = "localrag") -> FoundryLocalManager:
    FoundryLocalManager.initialize(Configuration(
        app_name=app_name,
        app_data_dir=config.APP_DATA_DIR,
        model_cache_dir=config.MODEL_CACHE_DIR,
    ))
    return FoundryLocalManager.instance


def register_hardware(manager: FoundryLocalManager) -> None:
    """Register missing GPU/NPU execution providers; variant selection depends on them, so this runs before any model is picked."""
    try:
        missing = [ep.name for ep in manager.discover_eps() if not ep.is_registered]
        if not missing:
            return
        print("  donanım hızlandırıcılar kaydediliyor...", end="", flush=True)
        result = manager.download_and_register_eps(names=missing)
        print(" " + (", ".join(result.registered_eps) or "yok (CPU kullanılacak)"))
    except Exception as exc:  # accelerators are optional
        print(f"\n  (donanım hızlandırıcılar atlandı: {exc})")


def provider_of(model) -> str | None:
    rt = model.info.runtime
    return rt.execution_provider if rt else None


def load_model(manager: FoundryLocalManager, alias: str, label: str, match_ep: str | None = None):
    """Find the model by alias, download it if needed (with progress) and load it.

    If match_ep is given and a variant for that provider exists, that one is used;
    mixing CUDA and TensorRT-RTX models in one process crashed natively on my machine.
    """
    model = manager.catalog.get_model(alias)
    if model is None:
        raise RuntimeError(f"'{alias}' Foundry Local kataloğunda bulunamadı.")
    if match_ep:
        same = [v for v in model.variants if provider_of(v) == match_ep]
        if same:
            model.select_variant(same[0])
    if not model.is_cached:
        model.download(lambda pct: _bar(label, pct))
        print()
    model.load()
    return model
