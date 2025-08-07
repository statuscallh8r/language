from error_types import ErrorType
from processor_base import unified_macros, unified_typecheck
from macro_registry import MacroContext
from node import Args

# Legacy registries - will be moved into steps
macros = unified_macros  # Use unified registry
typecheck = unified_typecheck  # Use unified registry

# TODO: Import-time registration removed - now handled by dependency injection in Macrocosm
# @macros.add("int")
def int_macro(ctx: MacroContext):
    args = ctx.compiler.get_metadata(ctx.node, Args)
    try:
        int(args)
    except ValueError:
        ctx.compiler.assert_(False, f"{args} must be a valid integer string.", ErrorType.INVALID_INT)
    ctx.expression_out.write(str(args))

# @typecheck.add("int")
def int_typecheck(ctx: MacroContext):
    return "int"

# @macros.add("float")
def float_macro(ctx: MacroContext):
    args = ctx.compiler.get_metadata(ctx.node, Args)
    try:
        float(args)
    except ValueError:
        ctx.compiler.assert_(False, f"{args} must be a valid float string.", ErrorType.INVALID_FLOAT)
    ctx.expression_out.write(str(args))

# @typecheck.add("float")
def int_typecheck(ctx: MacroContext):
    return "float"

# @macros.add("string", "regex")
def str_macro(ctx: MacroContext):
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
    from node import Macro
    macro = ctx.compiler.get_metadata(ctx.node, Macro)
    sep = '"' if macro == "string" else "/"
    ctx.expression_out.write(f'{sep}{s}{sep}')

# @typecheck.add("string")
def str_typecheck(ctx: MacroContext):
    return "str"

# @typecheck.add("regex")
def regex_typecheck(ctx: MacroContext):
    return "regex"

# Literal values that map directly to JavaScript
literally = {
    "true": "true",
    "false": "false",
    "break": "break",
    "continue": "continue",
    "dict": "{}",
    "return": "return"
}

# @macros.add(*[k for k in literally.keys()])
def literally_macro(ctx: MacroContext):
    # TODO. this isn't inherently expression_out... indeed most of these should be statement_out...
    from node import Macro
    macro = ctx.compiler.get_metadata(ctx.node, Macro)
    ctx.expression_out.write(literally[macro])