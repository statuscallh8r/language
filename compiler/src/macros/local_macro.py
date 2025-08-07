from dataclasses import replace
from processor_base import (
    MacroProcessingStep, singleton, js_field_access, 
    builtins, builtin_calls, DirectCall, seek_child_macro, cut, to_valid_js_ident,
    unified_macros, unified_typecheck, walk_upwards_for_local_definition
)
from macro_registry import MacroContext, MacroRegistry
from strutil import IndentedStringIO, Joiner
from node import Args, Macro, Params, Inject_code_start, SaneIdentifier, Target, ResolvedConvention, Node
from common_utils import collect_child_expressions, get_single_arg, get_two_args
from error_types import ErrorType
from logger import default_logger

# Legacy registries - will be moved into steps
macros = unified_macros  # Use unified registry
typecheck = unified_typecheck  # Use unified registry

# TODO: Import and bridge dependency injection version
from macro_base import di_registry, bridge_to_legacy, register_macro_manually

# NOTE: Macro registration is now handled in Macrocosm constructor to avoid import-time registration

# Preprocessing for 'local' macro - legacy function kept for backward compatibility
def local_preprocessing(ctx: MacroContext):
    """Preprocessing logic for 'local' macro - sets up identifiers"""
    desired_name = get_single_arg(ctx)
    actual_name = ctx.compiler.get_new_ident(desired_name)
    ctx.compiler.set_metadata(ctx.node, SaneIdentifier, actual_name)