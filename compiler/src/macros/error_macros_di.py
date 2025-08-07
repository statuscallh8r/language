from dataclasses import replace
from typing import Optional
from macro_registry import MacroContext
from strutil import IndentedStringIO
from macro_base import MacroInterface

class ErrorMacro(MacroInterface):
    """Handles the 'must_compile_error' macro"""
    
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for error macro"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Process must_compile_error children during emission to catch emission-time errors.
        
        The children are processed normally but their output is discarded using dummy outputs.
        Any errors generated during emission will be available for the verification step to check.
        """
        # Create dummy outputs to discard emission results
        dummy_statement_out = IndentedStringIO()
        dummy_expression_out = IndentedStringIO()
        
        # Process all children with dummy outputs to catch potential emission-time errors
        for child in ctx.node.children:
            child_ctx = replace(ctx, node=child, statement_out=dummy_statement_out, expression_out=dummy_expression_out)
            ctx.current_step.process_node(child_ctx)
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for error macro"""
        return None