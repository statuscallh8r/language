"""
Dependency Injection version of the local macro.

This shows the new cleaner approach where all macro logic is contained
in a single class with clear separation of concerns, using constructor-based
dependency injection to avoid circular import issues.
"""

from dataclasses import replace
from typing import Optional

from macro_base import MacroInterface
from macro_registry import MacroContext
from common_utils import collect_child_expressions, get_single_arg
from processor_base import seek_child_macro
from node import SaneIdentifier, FieldDemandType, Node
from error_types import ErrorType
from logger import default_logger


class LocalMacro(MacroInterface):
    """
    Local variable declaration macro using constructor-based dependency injection.
    
    Handles all aspects of local variable processing:
    - Preprocessing: identifier generation and scoping
    - JavaScript emission: variable declaration with optional initialization  
    - Type checking: type inference and validation
    """

    def preprocess(self, ctx: MacroContext) -> None:
        """Set up identifiers for local variable declaration"""
        desired_name = get_single_arg(ctx)
        actual_name = ctx.compiler.get_new_ident(desired_name)
        ctx.compiler.set_metadata(ctx.node, SaneIdentifier, actual_name)

    def process(self, ctx: MacroContext) -> Optional[str]:
        """Generate JavaScript for local variable declaration"""
        desired_name = get_single_arg(ctx)
        name = ctx.compiler.maybe_metadata(ctx.node, SaneIdentifier) or desired_name
        
        args = collect_child_expressions(ctx) if len(ctx.node.children) > 0 else []
        
        ctx.statement_out.write(f"let {name}")
        if len(args) > 0:
            ctx.statement_out.write(f" = {args[-1]}")
        ctx.statement_out.write(f"\n")
        ctx.expression_out.write(name)
        
        return None  # This doesn't return a type, typecheck handles that

    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Handle type checking for local variable declaration"""
        type_node = seek_child_macro(ctx.node, "type")

        received = None
        # Process children to get their types
        for child in ctx.node.children:
            child_ctx = replace(ctx, node=child)
            received = ctx.current_step.process_node(child_ctx) or received

        if not type_node:
            # TODO. this should be mandatory.
            if not seek_child_macro(ctx.node, "67lang:auto_type") or not received:
                return received
            type_node = Node(f"type {received}", ctx.node.pos, [])
        
        from strutil import cut
        _, demanded = cut(type_node.content, " ")
        default_logger.typecheck(f"{ctx.node.content} demanded {demanded} and was given {received} (children {[c.content for c in ctx.node.children]})")
        
        # Store the local variable type information in compiler metadata for upward walking
        ctx.compiler.set_metadata(ctx.node, FieldDemandType, demanded)
        
        # Also verify type matching if we have demanded type
        if demanded:
            if received is None:
                # If we have a demanded type but no received value, that's an error
                ctx.compiler.assert_(False, ctx.node, f"field demands {demanded} but is given None", ErrorType.MISSING_TYPE)
            elif received not in {"*", demanded}:
                ctx.compiler.assert_(False, ctx.node, f"field demands {demanded} but is given {received}", ErrorType.FIELD_TYPE_MISMATCH)
        
        return demanded or received or "*"