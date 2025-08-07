from dataclasses import replace
from processor_base import MacroProcessingStep, seek_child_macro, seek_parent_scope, unified_typecheck
from macro_registry import MacroContext
from strutil import cut
from node import Node, Macro
from common_utils import collect_child_types, get_single_arg, process_children_with_context
from logger import default_logger
from error_types import ErrorType

class TypeCheckingStep(MacroProcessingStep):
    """Handles type checking"""
    
    def __init__(self):
        super().__init__()
        # Use the unified typecheck registry
        self.macros = unified_typecheck
        
        # Initialize macros for this step
        self._register_macros()
        
    def _register_macros(self):
        """Register all type checking macros"""
        
        @self.macros.add("must_compile_error")
        def must_compile_error_typecheck(ctx: MacroContext):
            # Process children to generate type errors during type checking step
            for child in ctx.node.children:
                child_ctx = replace(ctx, node=child)
                ctx.current_step.process_node(child_ctx)
        
    def process_node(self, ctx: MacroContext) -> None:
        """Type check a single node"""
        macro = str(ctx.compiler.get_metadata(ctx.node, Macro))
        all_macros = self.macros.all()
        
        # Create a description for this node for indentation
        node_desc = f"node {macro}"
        if hasattr(ctx.node, 'content') and ctx.node.content:
            # Limit content preview to keep it readable
            content_preview = ctx.node.content[:50] + ("..." if len(ctx.node.content) > 50 else "")
            node_desc = f"node {macro}: {content_preview}"
        
        with default_logger.indent("typecheck", node_desc):
            if macro in all_macros:
                with ctx.compiler.safely:
                    return all_macros[macro](ctx)
            else:
                for child in ctx.node.children:
                    child_ctx = replace(ctx, node=child)
                    self.process_node(child_ctx)