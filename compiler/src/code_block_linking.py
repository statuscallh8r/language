# Legacy compatibility for code_block_linking.py
# The actual CodeBlockLinkingStep has been moved to steps/code_block_linking_step.py
# This file now only exists for backward compatibility during the refactor

# Re-export the step for backward compatibility
from steps.code_block_linking_step import CodeBlockLinkingStep, CodeBlockAssociator

# Note: The actual implementation has been moved to steps/code_block_linking_step.py
# This file now only exists for backward compatibility during the refactor