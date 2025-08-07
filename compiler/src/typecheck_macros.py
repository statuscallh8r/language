# Legacy registries for backward compatibility 
# These are now encapsulated within TypeCheckingStep in steps/typecheck_step.py
# This file can be removed once all references are updated

from processor_base import unified_typecheck

# Legacy registries - will be moved into steps
typecheck = unified_typecheck  # Use unified registry

# Note: The actual TypeCheckingStep implementation has been moved to steps/typecheck_step.py
# This file now only exists for backward compatibility during the refactor