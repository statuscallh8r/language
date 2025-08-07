from typing import Optional
from dataclasses import replace
from macro_base import MacroInterface, DependencyInjectedMacroRegistry
from macro_registry import MacroContext
from processor_base import (
    builtins, builtin_calls, DirectCall, walk_upwards_for_local_definition
)
from node import Args, SaneIdentifier, ResolvedConvention
from common_utils import collect_child_expressions
from error_types import ErrorType
from logger import default_logger

# TODO: Convert call macro to dependency injection pattern - eliminate import-time registration

class CallMacro(MacroInterface):
    """
    Handles 67lang:call macro - function calling operations with overload resolution
    """
    
    def __init__(self, registry: Optional[DependencyInjectedMacroRegistry] = None):
        self.registry = registry
        
    def preprocess(self, ctx: MacroContext) -> None:
        """Call macro requires no preprocessing"""
        pass
        
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Generate JavaScript code for function calls"""
        args_str = ctx.compiler.get_metadata(ctx.node, Args)
        args1 = args_str.split(" ")
        ident = ctx.compiler.get_new_ident("_".join(args1))
        
        # Try to get the resolved convention from metadata first
        try:
            resolved_conv = ctx.compiler.get_metadata(ctx.node, ResolvedConvention)
            convention = resolved_conv.convention
        except KeyError:
            # Fallback to the old method if metadata not available
            convention = self.resolve_convention(ctx)
        
        args = collect_child_expressions(ctx)

        call = convention.compile(args)

        ctx.statement_out.write(f"const {ident} = await {call}\n")
        ctx.expression_out.write(ident)
        return ident
        
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Handle type checking for function calls with overload resolution"""
        # First, determine the actual parameter types
        args: list[str | None] = []
        for child in ctx.node.children:
            # Find the typecheck step to handle type checking
            typecheck_step = ctx.current_step
            # Import here to avoid circular imports
            from steps.typecheck_step import TypeCheckingStep
            assert isinstance(typecheck_step, TypeCheckingStep)
            received = typecheck_step.process_node(replace(ctx, node=child))
            args.append(received)
        args = [a for a in args if a]

        # Now resolve the convention with actual parameter types
        convention = self.resolve_convention(ctx, args)
        
        # Store the resolved convention in metadata for later use during compilation
        ctx.compiler.set_metadata(ctx.node, ResolvedConvention, ResolvedConvention(convention=convention))

        if convention.demands:
            for received, demanded in zip(args, convention.demands):
                if "*" in {demanded, received}:
                    # TODO. generics!
                    continue
                default_logger.typecheck(f"{ctx.node.content} demanded {demanded} and was given {received}")
                # TODO - this should point to the child node that we received from, actually...
                ctx.compiler.assert_(received == demanded, ctx.node, f"argument demands {demanded} and is given {received}", ErrorType.ARGUMENT_TYPE_MISMATCH)

        return convention.returns or "*"
        
    def resolve_convention(self, ctx: MacroContext, actual_arg_types: list[str] = None):
        """Resolve calling convention for function calls with overload support"""
        args_str = ctx.compiler.get_metadata(ctx.node, Args)
        args = args_str.split(" ")
        ctx.compiler.assert_(len(args) == 1, ctx.node, "single argument, the function to call")
        
        fn = args[0]

        convention = None
        if fn in builtin_calls:
            overloads = builtin_calls[fn]
            if isinstance(overloads, list):
                # Multiple overloads - need to match by parameter types
                if actual_arg_types:
                    for overload in overloads:
                        if self._matches_signature(actual_arg_types, overload.demands):
                            convention = overload
                            break
                    else:
                        # No matching overload found, use the first one for now
                        # This will cause a type error later which is what we want
                        convention = overloads[0]
                else:
                    # No type information available, use first overload
                    convention = overloads[0]
            else:
                # Legacy single overload
                convention = overloads
        elif fn in builtins:
            convention = DirectCall(fn=builtins[fn], demands=None, receiver="_67lang", returns=None)
        else:
            res = walk_upwards_for_local_definition(ctx, fn)
            ctx.compiler.assert_(res != None, ctx.node, f"{fn} must refer to a defined function")
            fn = ctx.compiler.get_metadata(res.node, SaneIdentifier)
            convention = DirectCall(fn=fn, receiver=None, demands=None, returns=None)

        return convention
        
    def _matches_signature(self, actual_types: list[str], demanded_types: list[str]) -> bool:
        """Check if actual parameter types match the demanded signature"""
        if len(actual_types) != len(demanded_types):
            return False
        
        for actual, demanded in zip(actual_types, demanded_types):
            # "*" matches anything
            if demanded == "*" or actual == "*":
                continue
            if actual != demanded:
                return False
        return True