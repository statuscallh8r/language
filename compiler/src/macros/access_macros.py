from dataclasses import replace
from processor_base import (
    MacroProcessingStep, singleton, js_field_access, 
    builtins, builtin_calls, DirectCall, seek_child_macro, cut, to_valid_js_ident,
    unified_macros, unified_typecheck, walk_upwards_for_local_definition
)
from macro_registry import MacroContext, MacroRegistry
from strutil import IndentedStringIO, Joiner
from node import Args, Macro, Params, Inject_code_start, SaneIdentifier, Target, ResolvedConvention, Node
from common_utils import collect_child_expressions, get_single_arg, get_two_args
from error_types import ErrorType
from logger import default_logger

# Legacy registries - will be moved into steps
macros = unified_macros  # Use unified registry
typecheck = unified_typecheck  # Use unified registry



# TODO: Import-time registration removed - now handled by dependency injection in Macrocosm
# @macros.add("67lang:access_field")
def access_field(ctx: MacroContext):
    name, field = get_two_args(ctx, "first argument is object, second is field")
    res = walk_upwards_for_local_definition(ctx, name)
    ctx.compiler.assert_(res != None, ctx.node, f"{name} must access a defined function", ErrorType.NO_SUCH_LOCAL)
    name = ctx.compiler.maybe_metadata(res.node, SaneIdentifier) or name
    field_access = js_field_access(field)
    ident = ctx.compiler.get_new_ident("_".join([name, field]))

    args = collect_child_expressions(ctx)

    if len(args) > 0:
        ctx.compiler.assert_(len(args) == 1, ctx.node, "single child node for assignment")
        ctx.statement_out.write(f"{name}{field_access} = {args[-1]}\n")
    ctx.statement_out.write(f"const {ident} = await {name}{field_access}\n")
    ctx.expression_out.write(ident)

# @macros.add("67lang:access_index")
def access_index(ctx: MacroContext):
    name = get_single_arg(ctx, "single argument, the object into which we should index")
    res = walk_upwards_for_local_definition(ctx, name)
    ctx.compiler.assert_(res != None, ctx.node, f"{name} must access a defined function", ErrorType.NO_SUCH_LOCAL)
    name = ctx.compiler.maybe_metadata(res.node, SaneIdentifier) or name
    ident = ctx.compiler.get_new_ident(name) # TODO - pass index name too (doable...)

    args: list[str] = collect_child_expressions(ctx)

    ctx.compiler.assert_(len(args) >= 1, ctx.node, "first child used as indexing key")
    key = args[0]

    if len(args) > 1:
        ctx.compiler.assert_(len(args) == 2, ctx.node, "second child used for assignment")
        ctx.statement_out.write(f"{name}[{key}] = {args[1]}\n")

    ctx.statement_out.write(f"const {ident} = await {name}[{key}]\n")
    ctx.expression_out.write(ident)

# @macros.add("67lang:access_local")
def pil_access_local(ctx: MacroContext):
    desired_name = get_single_arg(ctx)
    res = walk_upwards_for_local_definition(ctx, desired_name)
    ctx.compiler.assert_(res != None, ctx.node, f"{desired_name} must access a defined local", ErrorType.NO_SUCH_LOCAL)
    actual_name = ctx.compiler.maybe_metadata(res.node, SaneIdentifier) or desired_name

    args = collect_child_expressions(ctx)

    if len(args) > 0:
        ctx.compiler.assert_(len(args) == 1, ctx.node, "single child used for assignment")
        ctx.statement_out.write(f"{actual_name} = {args[-1]}\n")

    ctx.expression_out.write(actual_name)

# TODO: local macro moved to local_macro.py - keeping this comment for tracking the separation

# TODO: 67lang:call macro moved to lang_call_macro.py - keeping this comment for tracking the separation

# TODO: exists macro moved to exists_macro.py - keeping this comment for tracking the separation

# Preprocessing for 'access' (a, an, access) macro
def access_preprocessing(ctx: MacroContext):
    """Preprocessing logic for 'access' macro - handles access chain unrolling"""
    from processor_base import builtin_calls
    from strutil import cut
    from node import Position, Indexers, Callers
    
    args = ctx.compiler.get_metadata(ctx.node, Args)
    parent = ctx.node.parent
    
    assert parent != None
    assert ctx.node.content.split(" ")[0] in {"a", "an", "access"}, ctx.node.content
    
    # contextually process substituting and calling modifiers among children
    indexers = {}
    callers = {}
    other_children = []
    
    for child in ctx.node.children:
        macro, _ = cut(child.content, " ")
        if macro == "where" and "is" in child.content:
            # New syntax: "where $id is"
            parts = child.content.split(" ")
            if len(parts) >= 3 and parts[2] == "is":
                key = parts[1]
            else:
                ctx.compiler.assert_(False, child, "where clause must be 'where $id is' or 'where $id takes'")
            
            default_logger.macro(f"substituting '{key}'")
            
            if len(child.children) >= 1:
                default_logger.debug(f"substituting '{key}' with {len(child.children)} child nodes")
                indexers[key] = child.children
            else:
                # shortcut for when the substitution is literal (i.e. most cases)
                default_logger.debug(f"substituting '{key}' with literal access")
                access = ctx.compiler.make_node(f"a {key}", ctx.node.pos or Position(0, 0), children=None)
                indexers[key] = [access]
        elif macro == "where" and "takes" in child.content:
            # New syntax: "where $id takes"
            parts = child.content.split(" ")
            if len(parts) >= 3 and parts[2] == "takes":
                key = parts[1]
            else:
                ctx.compiler.assert_(False, child, "where clause must be 'where $id is' or 'where $id takes'")
            
            default_logger.macro(f"calling '{key}' with {len(child.children)} children")
            
            ctx.compiler.assert_(len(child.children) >= 1, child, "calling must have at least one child")
            callers[key] = child.children
        else:
            other_children.append(child)
    
    steps: list[str] = args.split(" ")
    subs = indexers | callers
    last_chain_ident = None
    replace_with: list[Node] = []
    p0 = Position(0, 0)
    
    for step in steps:
        ident = ctx.compiler.get_new_ident(step)
        step_is_last = step == steps[-1]
        children = list(filter(lambda n: not n.content.startswith("noscope"), other_children))
        step_needs_call = step in builtin_calls or (step_is_last and len(children) > 1) or step in callers
        args1: list[Node] = []
        if step in subs:
            args1 = subs[step]
        if step_is_last:
            args1 += other_children

        local: list[Node] = []
        if step in indexers:
            # index
            local.append(ctx.compiler.make_node(f"67lang:access_index {last_chain_ident}", ctx.node.pos or p0, args1))
            for arg in args1:                        
                ctx.current_step.process_node(replace(ctx, node=arg))
        elif step_needs_call:
            # call or set
            self_arg = []
            if last_chain_ident:
                self_arg = [ctx.compiler.make_node(f"67lang:access_local {last_chain_ident}", ctx.node.pos or p0, [])]
            local.append(ctx.compiler.make_node(f"67lang:call {step}", ctx.node.pos or p0, self_arg + args1))
            local.append(ctx.compiler.make_node("67lang:auto_type", ctx.node.pos or p0, []))
            for arg in args1:
                ctx.current_step.process_node(replace(ctx, node=arg))
        else:
            # static field
            access = f"access_field {last_chain_ident}" if last_chain_ident else "access_local"
            local.append(ctx.compiler.make_node(f"67lang:{access} {step}", ctx.node.pos or p0, args1))
            local.append(ctx.compiler.make_node("67lang:auto_type", ctx.node.pos or p0, []))
            for arg in args1:
                ctx.current_step.process_node(replace(ctx, node=arg))

        local_node = ctx.compiler.make_node(f"local {ident}", ctx.node.pos or p0, children=local)
        last_chain_ident = ident
        replace_with.append(local_node)
        
    replace_with = list(filter(None, [ctx.compiler.make_node("noscope", ctx.node.pos or p0, replace_with[:-1]) if len(replace_with) > 1 else None, replace_with[-1]]))
    # print(f"replace child {ctx.node.content} of {parent.content} with {[c.content for c in replace_with]}")
    parent.replace_child(ctx.node, replace_with)

# TODO: local macro typecheck moved to local_macro.py - keeping this comment for tracking the separation

# Type checking for '67lang:access_local' macro
# @typecheck.add("67lang:access_local")
def access_local_typecheck(ctx: MacroContext):
    """Type checking for '67lang:access_local' macro"""
    first = get_single_arg(ctx, "single argument, the name of local")

    # Use utility function to collect child types
    from common_utils import collect_child_types
    types = collect_child_types(ctx)

    # Use upward walking to find local variable definition
    res = walk_upwards_for_local_definition(ctx, first)
    ctx.compiler.assert_(res != None, ctx.node, f"{first} must access a defined local", ErrorType.NO_SUCH_LOCAL)
    demanded = res.type
    
    if demanded and demanded != "*":
        if len(types) > 0:
            # TODO - support multiple arguments
            ctx.compiler.assert_(len(types) == 1, ctx.node, f"only support one argument for now (TODO!)", ErrorType.WRONG_ARG_COUNT)
            received = types[0]
            ctx.compiler.assert_(received in {demanded, "*"}, ctx.node, f"field demands {demanded} but is given {received}", ErrorType.FIELD_TYPE_MISMATCH)
        default_logger.typecheck(f"{ctx.node.content} demanded {demanded}")
        return demanded or "*"
    return "*"