from typing import Optional
from macro_base import MacroInterface, DependencyInjectedMacroRegistry
from macro_registry import MacroContext

# TODO: Convert comment macros to dependency injection pattern - eliminate import-time registration

class CommentMacro(MacroInterface):
    """
    Handles comment macros (#, //, /*, --, note) - comments are ignored during all processing steps
    TODO: Consider transferring comments to output in future
    """
    
    def __init__(self, registry: Optional[DependencyInjectedMacroRegistry] = None):
        self.registry = registry
        
    def preprocess(self, ctx: MacroContext) -> None:
        """Comments require no preprocessing"""
        pass
        
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Comments are ignored during JavaScript emission"""
        # Comments are skipped - no output generated
        pass
        
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Comments have no type"""
        # Comments are skipped - no type checking needed
        pass