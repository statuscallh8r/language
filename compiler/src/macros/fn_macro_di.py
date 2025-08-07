"""
Dependency Injection version of the fn and param macros.

This shows the new cleaner approach for complex macros that have multiple
related functions working together, using constructor-based dependency injection.
"""

from dataclasses import replace
from typing import Optional

from macro_base import MacroInterface
from macro_registry import MacroContext
from common_utils import get_single_arg
from processor_base import seek_child_macro, seek_all_child_macros
from node import SaneIdentifier, Params, Inject_code_start, Node, Macro
from strutil import Joiner
from logger import default_logger


class FnMacro(MacroInterface):
    """
    Function declaration macro using constructor-based dependency injection.
    
    Handles all aspects of function processing:
    - Preprocessing: identifier generation and parameter setup
    - JavaScript emission: function declaration with parameter handling  
    - No type checking needed for function declarations
    """

    def preprocess(self, ctx: MacroContext) -> None:
        """Set up identifiers and parameters for function declaration"""
        desired_name = get_single_arg(ctx)
        actual_name = ctx.compiler.get_new_ident(desired_name)
        ctx.compiler.set_metadata(ctx.node, SaneIdentifier, actual_name)
        
        # TODO - also hate this hack.
        for child in seek_all_child_macros(ctx.node, "param"):
            name = get_single_arg(replace(ctx, node=child))
            ctx.node.prepend_child(Node(f"67lang:assume_local_exists {name}", pos=ctx.node.pos, children=[]))

        for child in ctx.node.children:
            ctx.current_step.process_node(replace(ctx, node=child))

    def process(self, ctx: MacroContext) -> Optional[str]:
        """Generate JavaScript for function declaration"""
        name = get_single_arg(ctx)
        name = ctx.compiler.maybe_metadata(ctx.node, SaneIdentifier) or name
        ctx.statement_out.write(f"const {name} = async function (")
        joiner = Joiner(ctx.statement_out, ", \n")
        params_metadata = ctx.compiler.get_metadata(ctx.node, Params)
        params = params_metadata.mapping.items()
        if len(params) > 0:
            ctx.statement_out.write("\n")
        with ctx.statement_out:
            for k, _ in params:
                with joiner:
                    # just the name for now - this is JavaScript. in future we'd probably want JSDoc here too
                    ctx.statement_out.write(k)
        if len(params) > 0:
            ctx.statement_out.write("\n")
        ctx.statement_out.write(") ")
        next = seek_child_macro(ctx.node, "do")

        ctx.compiler.assert_(next != None, ctx.node, "must have a do block")

        inject = Inject_code_start()
        ctx.compiler.set_metadata(next, Inject_code_start, inject)
        ctx.statement_out.write("{")
        with ctx.statement_out:
            # TODO. this is absolute legacy. i'm fairly sure this does nothing by now
            for k, _ in params:
                inject.code.append(f"{k} = {k}\n")
            inner_ctx = replace(ctx, node=next)
            ctx.current_step.process_node(inner_ctx)
        ctx.statement_out.write("}")
        
        return None  # Functions don't return types, they are processed as statements


class ParamMacro(MacroInterface):
    """
    Parameter declaration macro using constructor-based dependency injection.
    
    Handles parameter registration within function declarations.
    """

    def preprocess(self, ctx: MacroContext) -> None:
        """Register parameters with the parent function"""
        args = get_single_arg(ctx, "param must have one argument - the name")
        parent = ctx.node.parent
        
        default_logger.macro(f"param '{args}'")
        
        assert parent != None
        ctx.compiler.assert_(len(ctx.node.children) == 0, ctx.node, "param must have no children")
        parent_macro = ctx.compiler.get_metadata(parent, Macro)
        ctx.compiler.assert_(parent_macro == "fn", ctx.node, "params must be inside fn")
        params = ctx.compiler.get_metadata(parent, Params)
        params.mapping[args] = True

    def process(self, ctx: MacroContext) -> Optional[str]:
        """No JavaScript emission needed for params - handled by fn macro"""
        return None

    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """No type checking needed for param declarations"""
        return None