import os
import sys

os.environ.setdefault("LANGCHAIN_DEBUG", "false")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")


def _apply_patch():
    try:
        import langchain

        if not hasattr(langchain, "debug"):
            langchain.debug = False
    except ImportError:
        import types

        langchain_mod = types.ModuleType("langchain")
        langchain_mod.debug = False
        if "langchain" not in sys.modules:
            sys.modules["langchain"] = langchain_mod

    try:
        import langchain_core.globals

        original_get_debug = langchain_core.globals.get_debug

        def patched_get_debug() -> bool:
            val = os.environ.get("LANGCHAIN_DEBUG", "false").lower()
            return val in ("true", "1", "t")

        if hasattr(langchain_core.globals, "get_debug"):
            langchain_core.globals.get_debug = patched_get_debug
    except (ImportError, AttributeError):
        pass


_apply_patch()
