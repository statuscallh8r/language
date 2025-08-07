"""
Dependency injection version of the if macro.

This shows the new cleaner approach where all if-related logic is contained
in a single class with clear separation of concerns, using constructor-based
dependency injection.
"""

from dataclasses import replace
from typing import Optional

from macro_base import MacroInterface
from macro_registry import MacroContext
from processor_base import seek_child_macro, seek_parent_scope
from strutil import IndentedStringIO
from common_utils import process_children_with_context


class IfMacro(MacroInterface):
    """
    If statement macro using constructor-based dependency injection.
    
    Handles all aspects of if processing:
    - JavaScript emission: conditional statement generation
    - No preprocessing needed for if statements
    - No type checking needed for if statements
    """

    def process(self, ctx: MacroContext) -> Optional[str]:
        """Generate JavaScript for if statement"""
        args: list[str] = []
        if len(ctx.node.children) > 0:
            # ctx.compiler.assert_(len(ctx.node.children) == 1, ctx.node, "single child, the value") TODO!
            for child in ctx.node.children:
                if child.content.startswith("then"): # TODO - ugly. bwah!
                    continue
                e = IndentedStringIO()
                ctx.current_step.process_node(replace(ctx, node=child, expression_out=e))
                args.append(e.getvalue())

        ctx.statement_out.write(f"if ({args[-1]})")
        ctx.statement_out.write(" {")
        with ctx.statement_out:
            node = seek_child_macro(ctx.node, "then")
            ctx.compiler.assert_(node != None, ctx.node, "must have a `then` block")
            inner_ctx = replace(ctx, node=node)
            ctx.current_step.process_node(inner_ctx)
        ctx.statement_out.write("}")
        
        return None  # If statements don't return types


class ThenMacro(MacroInterface):
    """
    Then block macro using constructor-based dependency injection.
    
    Handles the then block within if statements.
    """

    def process(self, ctx: MacroContext) -> Optional[str]:
        """No direct JavaScript emission - handled by parent if macro"""
        return None

    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Type checking for then blocks in if statements"""
        received = None
        for child in ctx.node.children:
            child_ctx = replace(ctx, node=child)
            received = ctx.current_step.process_node(child_ctx) or received
        
        # Return the type of the last expression in the then block
        # TODO: JavaScript emission needs to be updated to support expression-based if statements
        # Currently the if macro only generates statement-level conditionals, but in a functional
        # programming language if statements should be able to return values as expressions
        return received


class ElseMacro(MacroInterface):
    """
    Else block macro using constructor-based dependency injection.
    
    Handles the else block within if statements.
    """

    def process(self, ctx: MacroContext) -> Optional[str]:
        """No direct JavaScript emission - handled by scope macro"""
        return None

    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Type checking for else blocks in if statements"""
        received = None
        for child in ctx.node.children:
            child_ctx = replace(ctx, node=child)
            received = ctx.current_step.process_node(child_ctx) or received
        
        # Return the type of the last expression in the else block
        # TODO: JavaScript emission needs to be updated to support expression-based if statements
        # Currently the if macro only generates statement-level conditionals, but in a functional
        # programming language if statements should be able to return values as expressions
        return received