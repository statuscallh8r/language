from dataclasses import replace
from processor_base import seek_child_macro, unified_macros
from macro_registry import MacroContext
from strutil import IndentedStringIO

# TODO: Import-time registration removed - now handled by dependency injection in Macrocosm
# @unified_macros.add("while")
def while_loop(ctx: MacroContext):
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