# Legacy registries for backward compatibility 
# These are now encapsulated within PreprocessingStep in steps/preprocessing_step.py
# This file can be removed once all references are updated

from macro_registry import MacroRegistry

preprocessor = MacroRegistry()

# Import comment macros from comment_macros to avoid duplication
from macros.comment_macros import COMMENT_MACROS, code_linking, comments

# Register comment macros for preprocessing (for backward compatibility)
preprocessor.add(*COMMENT_MACROS)(comments)

# Note: The actual PreprocessingStep implementation has been moved to steps/preprocessing_step.py
# This file now only exists for backward compatibility during the refactor