from typing import Optional
from macro_registry import MacroContext
from macro_base import MacroInterface

class UtilityMacro(MacroInterface):
    """Handles utility macros: noop, type, 67lang:auto_type, 67lang:assume_local_exists"""
    
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for utility macros"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """JavaScript emission for utility macros - mostly no-ops"""
        # Most utility macros don't emit JavaScript
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for utility macros"""
        return None