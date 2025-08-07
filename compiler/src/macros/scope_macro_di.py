from dataclasses import replace
from typing import Optional
from processor_base import seek_child_macro, seek_parent_scope
from macro_registry import MacroContext
from node import Inject_code_start, Macro
from common_utils import process_children_with_context
from macro_base import MacroInterface

class ScopeMacro(MacroInterface):
    """Handles scope macros: do, then, else, 67lang:file"""
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for scope macros"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """JavaScript emission for scope macros"""
        macro = ctx.compiler.get_metadata(ctx.node, Macro)
        if macro in ["else"]:
            ctx.statement_out.write(f"{macro} ")

        ctx.statement_out.write("{\n")
        with ctx.statement_out:
            ctx.statement_out.write("const parent_scope = scope\n")
            ctx.statement_out.write("{\n")
            with ctx.statement_out:
                ctx.statement_out.write("const scope = _67lang.scope(parent_scope)\n")
                inject = ctx.compiler.maybe_metadata(ctx.node, Inject_code_start)
                if inject:
                    for code in inject.code:
                        ctx.statement_out.write(code)
                for child in ctx.node.children:
                    child_ctx = replace(ctx, node=child)
                    child_ctx.current_step.process_node(child_ctx)
                    ctx.statement_out.write("\n")
            ctx.statement_out.write("}\n")
        ctx.statement_out.write("} ")
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Type checking for scope macros (do, 67lang:file)"""
        parent = seek_parent_scope(ctx.node)
        # Temporarily disable scope metadata - implement walking upwards approach later
        # ctx.compiler.set_metadata(ctx.node, Scope, Scope(parent=parent))
        process_children_with_context(ctx, ctx.current_step)
        return None

class DoMacro(ScopeMacro):
    """Specific handler for 'do' macro with type checking"""
    pass

class ThenMacro(ScopeMacro):
    """Specific handler for 'then' macro"""
    pass

class ElseMacro(ScopeMacro):
    """Specific handler for 'else' macro"""  
    pass

class FileMacro(ScopeMacro):
    """Specific handler for '67lang:file' macro with type checking"""
    pass