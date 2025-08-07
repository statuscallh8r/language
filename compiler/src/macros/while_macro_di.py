from dataclasses import replace
from typing import Optional
from processor_base import seek_child_macro
from macro_registry import MacroContext
from strutil import IndentedStringIO
from macro_base import MacroInterface

class WhileMacro(MacroInterface):
    def __init__(self, registry: Optional['DependencyInjectedMacroRegistry'] = None):
        self.registry = registry
    
    def preprocess(self, ctx: MacroContext) -> None:
        """No preprocessing needed for while loop"""
        pass
    
    def process(self, ctx: MacroContext) -> Optional[str]:
        """JavaScript emission for while loop macro"""
        ctx.statement_out.write("while(true) {")
        with ctx.statement_out:
            ctx.compiler.assert_(len(ctx.node.children) == 2, ctx.node, "must have two children")
            node = ctx.node.children[0]
            out = IndentedStringIO()
            inner_ctx = replace(ctx, node=node, expression_out=out)
            ctx.current_step.process_node(inner_ctx)

            ctx.statement_out.write(f"if (!{out.getvalue()}) ")
            ctx.statement_out.write("{ break; }\n")

            node = seek_child_macro(ctx.node, "do")
            ctx.compiler.assert_(node != None, ctx.node, "must have a `do` block")
            inner_ctx = replace(ctx, node=node)
            ctx.current_step.process_node(inner_ctx)
        ctx.statement_out.write("}")
        return None
    
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No specific type checking needed for while loop"""
        return None