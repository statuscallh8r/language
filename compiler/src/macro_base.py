"""
Base classes for the dependency injection approach to macros.

This module provides the foundation for a cleaner macro architecture where
macros are classes with clear interfaces rather than standalone functions.
Both old and new approaches can coexist during the transition.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from macro_registry import MacroContext, MacroRegistry

class MacroInterface(ABC):
    """Base interface for all macros using dependency injection approach"""
    
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        """Constructor for dependency injection - registry can be injected if needed"""
        self.registry = registry
    
    @abstractmethod
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Process the macro and return any type information"""
        pass
    
    def preprocess(self, ctx: MacroContext) -> None:
        """Optional preprocessing step - override if needed"""
        pass
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Optional type checking step - override if needed"""
        return None

@dataclass
class MacroDefinition:
    """Definition of a macro with all its processing steps"""
    name: str
    macro_class: type[MacroInterface]
    aliases: list[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []

class DependencyInjectedMacroRegistry:
    """Registry for dependency injection based macros"""
    
    def __init__(self):
        self._macros: Dict[str, MacroDefinition] = {}
        self._instances: Dict[str, MacroInterface] = {}
    
    def register(self, definition: MacroDefinition) -> None:
        """Register a macro definition"""
        # Register the main name
        self._macros[definition.name] = definition
        
        # Register all aliases
        for alias in definition.aliases:
            self._macros[alias] = definition
    
    def get_instance(self, name: str) -> MacroInterface:
        """Get a macro instance, creating it if needed"""
        if name not in self._instances:
            if name not in self._macros:
                raise ValueError(f"Unknown macro: {name}")
            
            definition = self._macros[name]
            # Pass this registry to the macro constructor for proper dependency injection
            self._instances[name] = definition.macro_class(registry=self)
        
        return self._instances[name]
    
    def has_macro(self, name: str) -> bool:
        """Check if a macro is registered"""
        return name in self._macros
    
    def get_all_names(self) -> list[str]:
        """Get all registered macro names"""
        return list(self._macros.keys())

# Global dependency injection registry
di_registry = DependencyInjectedMacroRegistry()

def register_macro_manually(name: str, macro_class: type[MacroInterface], aliases: list[str] = None):
    """Manual registration function to avoid import-time registration"""
    definition = MacroDefinition(name=name, macro_class=macro_class, aliases=aliases or [])
    di_registry.register(definition)

def register_macro(name: str, aliases: list[str] = None):
    """Decorator to register a macro class with dependency injection - DEPRECATED
    
    Use register_macro_manually() instead to avoid import-time registration issues.
    """
    def decorator(cls: type[MacroInterface]) -> type[MacroInterface]:
        definition = MacroDefinition(name=name, macro_class=cls, aliases=aliases or [])
        di_registry.register(definition)
        return cls
    return decorator

class MacroAdapter:
    """Adapter to make dependency injection macros work with legacy registries"""
    
    def __init__(self, macro_name: str, step_type: str = "process"):
        self.macro_name = macro_name
        self.step_type = step_type
    
    def __call__(self, ctx: MacroContext) -> Optional[str]:
        instance = di_registry.get_instance(self.macro_name)
        
        if self.step_type == "process":
            return instance.process(ctx)
        elif self.step_type == "preprocess":
            instance.preprocess(ctx)
            return None
        elif self.step_type == "typecheck":
            return instance.typecheck(ctx)
        else:
            raise ValueError(f"Unknown step type: {self.step_type}")

def bridge_to_legacy(registry: MacroRegistry, macro_name: str, step_type: str = "process"):
    """Bridge a dependency injection macro to a legacy registry"""
    adapter = MacroAdapter(macro_name, step_type)
    # Don't raise error if already registered - allow overriding for migration
    if macro_name in registry._registry:
        print(f"Warning: Overriding existing macro '{macro_name}' with DI version")
    registry._registry[macro_name] = adapter