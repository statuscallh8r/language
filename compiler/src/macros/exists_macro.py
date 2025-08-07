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

@macros.add("exists")
def exists_inside(ctx: MacroContext):
    # look for inside modifier among children
    target = None
    other_children = []
    
    for child in ctx.node.children:
        macro, _ = cut(child.content, " ")
        if macro == "inside":
            args_str = ctx.compiler.get_metadata(child, Args)
            ctx.compiler.assert_(args_str.strip() == "", child, "inside must have no arguments")
            ctx.compiler.assert_(len(child.children) == 1, child, "inside must have one child")
            target = child.children[0]
            default_logger.macro(f"inside modifier found, target set to: {target.content}")
        else:
            other_children.append(child)
    
    ctx.compiler.assert_(target is not None, ctx.node, "exists must have an inside modifier")
    ctx.compiler.compile_fn_call(ctx, f"await _67lang.exists_inside(", [target] + other_children)