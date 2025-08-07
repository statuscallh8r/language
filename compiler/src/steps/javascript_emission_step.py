from dataclasses import replace
from processor_base import MacroProcessingStep, js_lib, unified_macros
from macro_registry import MacroContext
from strutil import IndentedStringIO
from contextlib import contextmanager
from node import Macro
from logger import default_logger
from error_types import ErrorType

class JavaScriptEmissionStep(MacroProcessingStep):
    """Handles JavaScript code emission"""
    
    def __init__(self):
        super().__init__()
        # Use the unified macros registry
        self.macros = unified_macros
        
    def process_node(self, ctx: MacroContext) -> None:
        """Process a single node for JavaScript emission"""            
        macro = str(ctx.compiler.get_metadata(ctx.node, Macro))
        all_macros = self.macros.all()
        
        default_logger.codegen(f"emitting JavaScript for macro: {macro}")

        # --- cursed Python begins ---

        @contextmanager
        def possibly_wrapped(ctx: MacroContext):
            # no wrapping needed
            yield ctx

        if ctx.node.content == "67lang:solution":
            default_logger.codegen("wrapping solution in JavaScript runtime setup")
            @contextmanager
            def definitely_wrapped(ctx: MacroContext):
                out = IndentedStringIO()
                out.write(js_lib + "\n\n")
                # need to wrap this crap in async because browsers are GARBAGE 
                # (top level await only in modules? why?!)
                default_logger.codegen("adding async wrapper for browser compatibility")
                out.write("void (async () => {\n")
                with out:
                    out.write("'use strict';\n")
                    out.write("const scope = globalThis;\n")
                    yield replace(ctx, statement_out=out, expression_out=out)
                out.write("\n})();")
                ctx.compiler._js_output = out.getvalue()
                default_logger.codegen(f"JavaScript output generated: {len(out.getvalue())} characters")
            possibly_wrapped = definitely_wrapped

        # --- cursed Python ends ---

        with possibly_wrapped(ctx) as ctx:
            if macro in all_macros:
                default_logger.codegen(f"applying JavaScript emission macro: {macro}")
                with ctx.compiler.safely:
                    all_macros[macro](ctx)
            else:
                # Only generate unknown macro error if this is a real non-empty macro name
                # Skip empty or whitespace-only macros which are likely parsing artifacts
                if macro and macro.strip():
                    default_logger.codegen(f"ERROR: unknown macro {macro}")
                    # Generate a compile error for unknown macros
                    ctx.compiler.compile_error(ctx.node, 
                        f"unknown macro '{macro}' - is this supposed to exist? did you maybe typo something?", 
                        ErrorType.INVALID_MACRO)
                else:
                    default_logger.codegen(f"skipping empty/invalid macro: '{macro}'")