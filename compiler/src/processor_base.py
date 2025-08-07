"""
Minimal processor base - Step 4 compiler rewrite
Stubs for the original processor infrastructure
"""

class MacroRegistry:
    """Minimal macro registry stub"""
    
    def __init__(self):
        self._macros = {}
        
    def all(self):
        return self._macros
        
    def register(self, name, macro):
        self._macros[name] = macro


# Create global registry instances that main.py expects
unified_macros = MacroRegistry()
unified_typecheck = MacroRegistry()