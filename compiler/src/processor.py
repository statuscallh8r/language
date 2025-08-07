# Refactored processor.py - now imports from individual macro modules
# Import all the base components
from processor_base import *

# Import macro processing steps
from steps.preprocessing_step import PreprocessingStep
from steps.code_block_linking_step import CodeBlockLinkingStep
from steps.typecheck_step import TypeCheckingStep  
from steps.javascript_emission_step import JavaScriptEmissionStep

# Import all the individual macro registrations
from literal_macros import macros as literal_macros_registry, typecheck as literal_typecheck_registry
from macros.access_macros import macros as access_macros_registry, typecheck as access_typecheck_registry
# TODO: Import the separated local macro to ensure registration
import macros.local_macro  # Import to ensure local macro registration
import macros  # Import the new macros package to ensure registration
from typecheck_macros import typecheck as typecheck_macros_registry

from macrocosm import Macrocosm

# Merge all the registries for backward compatibility
macros = MacroRegistry()
typecheck = MacroRegistry()

# Merge literal macros
for name, handler in literal_macros_registry.all().items():
    macros._registry[name] = handler

for name, handler in literal_typecheck_registry.all().items():
    typecheck._registry[name] = handler
    
# Merge access macros  
for name, handler in access_macros_registry.all().items():
    macros._registry[name] = handler
    
for name, handler in access_typecheck_registry.all().items():
    typecheck._registry[name] = handler

# Note: control flow macros now register directly with unified_macros

# Merge type check macros
for name, handler in typecheck_macros_registry.all().items():
    typecheck._registry[name] = handler

# Legacy singleton instances for backward compatibility - these are created in their respective modules
# TODO: Import from separated lang_call_macro instead of access_macros
from macros.lang_call_macro import Macro_67lang_call
