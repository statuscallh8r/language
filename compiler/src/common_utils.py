"""
common utility functions to reduce code duplication across the compiler.
"""

from dataclasses import replace
from typing import List, Optional
from strutil import IndentedStringIO, cut
from macro_registry import MacroContext
from node import Args
from logger import default_logger

def collect_child_expressions(ctx: MacroContext) -> List[str]:
    """
    collect expressions from all child nodes by processing them.
    this pattern was repeated many times across different macro handlers.
    
    Args:
        ctx: the macro context
    
    Returns:
        list of expression strings from children
    """
    expressions: List[Optional[str]] = []
    
    default_logger.debug(f"collecting expressions from {len(ctx.node.children)} children")
    
    for i, child in enumerate(ctx.node.children):
        with default_logger.indent("debug", f"processing child {i}: {child.content}"):
            expression_out = IndentedStringIO()
            child_ctx = replace(ctx, node=child, expression_out=expression_out)
            ctx.current_step.process_node(child_ctx)
            expr_value = expression_out.getvalue()
            expressions.append(expr_value)
            default_logger.debug(f"child {i} produced: '{expr_value}'")
    
    result = [expr for expr in expressions if expr]
    default_logger.debug(f"filtered {len(expressions)} -> {len(result)} non-empty expressions")
    return result

def collect_child_types(ctx: MacroContext) -> List[str]:
    """
    collect type information from all child nodes during type checking.
    this pattern was also repeated in type checking code.
    
    Args:
        ctx: the macro context (should be in type checking step)
    
    Returns:
        list of type strings from children
    """
    from steps.typecheck_step import TypeCheckingStep
    
    assert isinstance(ctx.current_step, TypeCheckingStep), "collect_child_types called outside TypeCheckingStep"
        
    types: List[Optional[str]] = []
    
    default_logger.typecheck(f"collecting types from {ctx.node.content}")
    
    for i, child in enumerate(ctx.node.children):
        with default_logger.indent("typecheck", f"type checking child {i}: {child.content}"):
            child_ctx = replace(ctx, node=child)
            child_type = ctx.current_step.process_node(child_ctx)
            types.append(child_type)
            default_logger.typecheck(f"child {i} has type: '{child_type}'")
    
    result = [t for t in types if t]
    default_logger.typecheck(f"filtered {len(types)} -> {len(result)} non-empty types")
    return result

def process_children_with_context(ctx: MacroContext, step_processor) -> None:
    """
    process all children with the given step processor.
    another common pattern for walking the tree.
    
    Args:
        ctx: the macro context  
        step_processor: the processing step to apply to each child
    """
    default_logger.debug(f"processing children of {ctx.node.content} with {step_processor.__class__.__name__}")
    
    for i, child in enumerate(ctx.node.children):
        with default_logger.indent("debug", f"processing child {i}: {child.content}"):
            with ctx.compiler.safely:
                child_ctx = replace(ctx, node=child)
                step_processor.process_node(child_ctx)

def get_args_string(ctx: MacroContext) -> str:
    """
    get the arguments string from a node's metadata.
    this is done so frequently it deserves its own utility.
    
    Args:
        ctx: the macro context
        
    Returns:
        the arguments string
    """
    args = ctx.compiler.get_metadata(ctx.node, Args)
    default_logger.debug(f"extracted args: '{args}'")
    return args

def get_single_arg(ctx: MacroContext, error_msg: str = "must have a single argument") -> str:
    """
    get a single argument from a node, asserting there's exactly one.
    another very common pattern.
    
    Args:
        ctx: the macro context
        error_msg: error message if assertion fails
        
    Returns:
        the single argument string
    """
    args = get_args_string(ctx)
    first, extra = cut(args, " ")
    ctx.compiler.assert_(extra == "", ctx.node, error_msg)
    default_logger.debug(f"validated single arg: '{first}'")
    return first

def get_two_args(ctx: MacroContext, error_msg: str = "must have exactly two arguments") -> tuple[str, str]:
    """
    get exactly two arguments from a node.
    
    Args:
        ctx: the macro context
        error_msg: error message if assertion fails
        
    Returns:
        tuple of the two argument strings
    """
    args = get_args_string(ctx)
    args_list = args.split(" ")
    ctx.compiler.assert_(len(args_list) == 2, ctx.node, error_msg)
    default_logger.debug(f"validated two args: '{args_list[0]}', '{args_list[1]}'")
    return args_list[0], args_list[1]


import inspect
from functools import wraps

def print_with_callback(callback):
    def decorator(func):
        sig = inspect.signature(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            result = func(*args, **kwargs)
            # Combine all positional and keyword arguments, followed by result
            all_args = list(bound.args)
            # If you want to include keyword arguments as well, add them in desired order
            all_args.extend(bound.kwargs.values())
            all_args.append(result)
            output = callback(*all_args)
            print(output)
            return result
        return wrapper
    return decorator