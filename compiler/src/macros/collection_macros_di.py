from typing import Optional
from macro_registry import MacroContext
from macro_base import MacroInterface

class CollectionMacro(MacroInterface):
    """Handles the 'list' macro"""
    
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for collection macro"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Handle list macro - iterate all children, collect their expressions, emit [expr1, expr2, expr3...]"""
        if not ctx.node.children:
            ctx.expression_out.write("[]")
            return None
        
        from common_utils import collect_child_expressions
        expressions = collect_child_expressions(ctx)
        ctx.expression_out.write(f"[{', '.join(expressions)}]")
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for collection macro"""
        return None