from typing import Optional
from macro_base import MacroInterface, DependencyInjectedMacroRegistry
from macro_registry import MacroContext
from error_types import ErrorType
from node import Args, Macro

# TODO: Convert literal value macros to dependency injection pattern - eliminate import-time registration

class LiteralValueMacro(MacroInterface):
    """
    Handles literal value macros (int, float, string, regex, and literal constants)
    """
    
    def __init__(self, registry: Optional[DependencyInjectedMacroRegistry] = None):
        self.registry = registry
        
        # Literal values that map directly to JavaScript
        self.literally = {
            "true": "true",
            "false": "false", 
            "break": "break",
            "continue": "continue",
            "dict": "{}",
            "return": "return"
        }
        
    def preprocess(self, ctx: MacroContext) -> None:
        """Literal values require no preprocessing"""
        pass
        
    def process(self, ctx: MacroContext) -> Optional[str]:
        """Generate JavaScript code for literal values"""
        macro = ctx.compiler.get_metadata(ctx.node, Macro)
        
        if macro == "int":
            return self._process_int(ctx)
        elif macro == "float":
            return self._process_float(ctx)
        elif macro in ["string", "regex"]:
            return self._process_string_regex(ctx)
        elif macro in self.literally:
            return self._process_literal(ctx, macro)
        
        return None
        
    def typecheck(self, ctx: MacroContext) -> Optional[str]:
        """Return type information for literal values"""
        macro = ctx.compiler.get_metadata(ctx.node, Macro)
        
        if macro == "int":
            return "int"
        elif macro == "float":
            return "float"
        elif macro == "string":
            return "str"
        elif macro == "regex":
            return "regex"
        # Other literals don't have explicit types in the current system
        
        return None
        
    def _process_int(self, ctx: MacroContext) -> str:
        """Process integer literal"""
        args = ctx.compiler.get_metadata(ctx.node, Args)
        try:
            int(args)
        except ValueError:
            ctx.compiler.assert_(False, f"{args} must be a valid integer string.", ErrorType.INVALID_INT)
        ctx.expression_out.write(str(args))
        return str(args)
        
    def _process_float(self, ctx: MacroContext) -> str:
        """Process float literal"""
        args = ctx.compiler.get_metadata(ctx.node, Args)
        try:
            float(args)
        except ValueError:
            ctx.compiler.assert_(False, f"{args} must be a valid float string.", ErrorType.INVALID_FLOAT)
        ctx.expression_out.write(str(args))
        return str(args)
        
    def _process_string_regex(self, ctx: MacroContext) -> str:
        """Process string or regex literal"""
        s: str = ctx.compiler.get_metadata(ctx.node, Args)
        if len(s) == 0:
            # multiline string case - collect content from children
            lines = []
            for child in ctx.node.children:
                if child.content:
                    lines.append(child.content)
            s = "\n".join(lines)
        else:
            delim = s[0]
            ctx.compiler.assert_(s.endswith(delim), ctx.node, "must be delimited on both sides with the same character")
            s = s.removeprefix(delim).removesuffix(delim)
        s = s.replace("\n", "\\n")
        s = s.replace('"', '\\"')  # escape quotes during JS string emission
        
        macro = ctx.compiler.get_metadata(ctx.node, Macro)
        sep = '"' if macro == "string" else "/"
        result = f'{sep}{s}{sep}'
        ctx.expression_out.write(result)
        return result
        
    def _process_literal(self, ctx: MacroContext, macro: str) -> str:
        """Process literal constants (true, false, break, etc.)"""
        # TODO. this isn't inherently expression_out... indeed most of these should be statement_out...
        result = self.literally[macro]
        ctx.expression_out.write(result)
        return result