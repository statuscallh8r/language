from typing import Optional
from macro_registry import MacroContext
from node import Macro
from macro_base import MacroInterface

class BuiltinMacro(MacroInterface):
    """Handles all builtin macros (print, add, concat, etc.) via dependency injection"""
    
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
        # Import builtins mapping here to avoid circular import issues
        from processor_base import builtins
        self.builtins = builtins
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for builtin macros"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """JavaScript emission for builtin macros"""
        macro = ctx.compiler.get_metadata(ctx.node, Macro)
        if macro in self.builtins:
            ctx.compiler.compile_fn_call(ctx, f"await _67lang.{self.builtins[macro]}(", ctx.node.children)
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for builtin macros"""
        return None