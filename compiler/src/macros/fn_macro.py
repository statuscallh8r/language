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

# Preprocessing for 'fn' macro - legacy function kept for backward compatibility
def fn_preprocessing(ctx: MacroContext):
    """Preprocessing logic for 'fn' macro - sets up identifiers and parameters"""
    from processor_base import seek_all_child_macros
    
    desired_name = get_single_arg(ctx)
    actual_name = ctx.compiler.get_new_ident(desired_name)
    ctx.compiler.set_metadata(ctx.node, SaneIdentifier, actual_name)
    
    # TODO - also hate this hack.
    for child in seek_all_child_macros(ctx.node, "param"):
        name = get_single_arg(replace(ctx, node=child))
        ctx.node.prepend_child(Node(f"67lang:assume_local_exists {name}", pos=ctx.node.pos, children=[]))

    for child in ctx.node.children:
        ctx.current_step.process_node(replace(ctx, node=child))

# Preprocessing for 'param' macro - legacy function kept for backward compatibility
def param_preprocessing(ctx: MacroContext):
    """Preprocessing logic for 'param' macro - registers parameters"""
    args = get_single_arg(ctx, "param must have one argument - the name")
    parent = ctx.node.parent
    
    default_logger.macro(f"param '{args}'")
    
    assert parent != None
    ctx.compiler.assert_(len(ctx.node.children) == 0, ctx.node, "param must have no children")
    parent_macro = ctx.compiler.get_metadata(parent, Macro)
    ctx.compiler.assert_(parent_macro == "fn", ctx.node, "params must be inside fn")
    params = ctx.compiler.get_metadata(parent, Params)
    params.mapping[args] = True