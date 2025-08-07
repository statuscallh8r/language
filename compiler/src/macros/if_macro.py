from dataclasses import replace
from processor_base import seek_child_macro, unified_macros, unified_typecheck, seek_parent_scope
from macro_registry import MacroContext
from strutil import IndentedStringIO
from common_utils import process_children_with_context

# TODO: Import and bridge dependency injection version
from macro_base import di_registry, bridge_to_legacy, register_macro_manually

# NOTE: Macro registration is now handled in Macrocosm constructor to avoid import-time registration