from dataclasses import replace
from typing import Optional
from macro_registry import MacroContext
from macro_base import MacroInterface

class NoscopeMacro(MacroInterface):
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for noscope"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """JavaScript emission for noscope macro"""
        for child in ctx.node.children:
            child_ctx = replace(ctx, node=child)
            child_ctx.current_step.process_node(child_ctx)
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for noscope"""
        return None