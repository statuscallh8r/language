from contextlib import contextmanager
from typing import Any, Sequence
from io import StringIO
from node import Node, Position, Macro, Args
from strutil import IndentedStringIO, Joiner
from processor_base import MacroProcessingStep, MacroAssertFailed, to_valid_js_ident
from macro_registry import MacroContext
from steps.preprocessing_step import PreprocessingStep
from steps.code_block_linking_step import CodeBlockLinkingStep  
from steps.typecheck_step import TypeCheckingStep
from steps.must_compile_error_step import MustCompileErrorVerificationStep
from steps.javascript_emission_step import JavaScriptEmissionStep
from logger import default_logger

class Macrocosm:
    def __init__(self):
        self.nodes: list[Node] = []
        # TODO. incremental is good enough for now, but we'll have to stabilize it.
        #  the last thing you would want is the entire output changing because you added a statement. that's a lot of
        #  unnecessary diff. best way to solve this that i see is to make this block-scoped,
        #  so that each block gets its own incremental. a bit harder, though.
        self.incremental_id = 0
        self.compile_errors: list[dict[str, Any]] = []
        self._js_output: str = ""
        
        # Metadata tracking system to replace TypeMap
        self._node_metadata: dict[int, dict[type, Any]] = {}
        
        # Initialize the processing pipeline
        self.processing_steps: list[MacroProcessingStep] = [
            PreprocessingStep(),
            CodeBlockLinkingStep(), 
            TypeCheckingStep(),
            JavaScriptEmissionStep(),
            MustCompileErrorVerificationStep()
        ]
        
        # Set up dependency injection macros - moved from import-time registration
        self._setup_dependency_injection_macros()
    
    def _setup_dependency_injection_macros(self):
        """Set up all dependency injection based macros - centralized to avoid import-time registration"""
        from macro_base import register_macro_manually, bridge_to_legacy
        from processor_base import unified_macros, unified_typecheck
        
        # Set up local macro
        try:
            from macros.local_macro_di import LocalMacro
            register_macro_manually("local", LocalMacro)
            bridge_to_legacy(unified_macros, "local", "process")
            bridge_to_legacy(unified_typecheck, "local", "typecheck")
        except ImportError as e:
            raise RuntimeError(f"Failed to register local macro: {e}")
        
        # Set up fn and param macros  
        try:
            from macros.fn_macro_di import FnMacro, ParamMacro
            register_macro_manually("fn", FnMacro)
            register_macro_manually("param", ParamMacro, aliases=[])
            bridge_to_legacy(unified_macros, "fn", "process")
            bridge_to_legacy(unified_macros, "param", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register fn/param macros: {e}")
            
        # Set up if, then, and else macros
        try:
            from macros.if_macro_di import IfMacro, ThenMacro, ElseMacro
            register_macro_manually("if", IfMacro)
            register_macro_manually("then", ThenMacro)
            register_macro_manually("else", ElseMacro)
            bridge_to_legacy(unified_macros, "if", "process")
            bridge_to_legacy(unified_typecheck, "then", "typecheck")
            bridge_to_legacy(unified_typecheck, "else", "typecheck")
        except ImportError as e:
            raise RuntimeError(f"Failed to register if/then/else macros: {e}")
            
        # Set up builtin macros
        try:
            from macros.builtin_macros_di import BuiltinMacro
            from processor_base import builtins
            # Register all builtin operations with the same macro class
            for builtin_name in builtins.keys():
                register_macro_manually(builtin_name, BuiltinMacro)
                bridge_to_legacy(unified_macros, builtin_name, "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register builtin macros: {e}")
            
        # Set up collection macros
        try:
            from macros.collection_macros_di import CollectionMacro
            register_macro_manually("list", CollectionMacro)
            bridge_to_legacy(unified_macros, "list", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register collection macros: {e}")
            
        # Set up utility macros
        try:
            from macros.utility_macros_di import UtilityMacro
            utility_macro_names = ["noop", "type", "67lang:auto_type", "67lang:assume_local_exists"]
            for utility_name in utility_macro_names:
                register_macro_manually(utility_name, UtilityMacro)
                bridge_to_legacy(unified_macros, utility_name, "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register utility macros: {e}")
            
        # Set up while and for loop macros
        try:
            from macros.while_macro_di import WhileMacro
            from macros.for_macro_di import ForMacro
            register_macro_manually("while", WhileMacro)
            register_macro_manually("for", ForMacro)
            bridge_to_legacy(unified_macros, "while", "process")
            bridge_to_legacy(unified_macros, "for", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register while/for macros: {e}")
            
        # Set up error macros
        try:
            from macros.error_macros_di import ErrorMacro
            register_macro_manually("must_compile_error", ErrorMacro)
            bridge_to_legacy(unified_macros, "must_compile_error", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register error macros: {e}")
            
        # Set up exists macro
        try:
            from macros.exists_macro_di import ExistsMacro
            register_macro_manually("exists", ExistsMacro)
            bridge_to_legacy(unified_macros, "exists", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register exists macro: {e}")
            
        # Set up solution macro
        try:
            from macros.solution_macro_di import SolutionMacro
            register_macro_manually("67lang:solution", SolutionMacro)
            bridge_to_legacy(unified_macros, "67lang:solution", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register solution macro: {e}")
            
        # Set up comment macros
        try:
            from macros.comment_macros_di import CommentMacro
            comment_macro_names = ["#", "//", "/*", "--", "note"]
            for comment_name in comment_macro_names:
                register_macro_manually(comment_name, CommentMacro)
                bridge_to_legacy(unified_macros, comment_name, "process")
                bridge_to_legacy(unified_typecheck, comment_name, "typecheck")
        except ImportError as e:
            raise RuntimeError(f"Failed to register comment macros: {e}")
            
        # Set up literal value macros
        try:
            from macros.literal_value_macros_di import LiteralValueMacro
            # Literal value types
            literal_types = ["int", "float", "string", "regex"]
            for literal_type in literal_types:
                register_macro_manually(literal_type, LiteralValueMacro)
                bridge_to_legacy(unified_macros, literal_type, "process")
                bridge_to_legacy(unified_typecheck, literal_type, "typecheck")
                
            # Literal constants that map directly to JavaScript
            literal_constants = ["true", "false", "break", "continue", "dict", "return"]
            for literal_const in literal_constants:
                register_macro_manually(literal_const, LiteralValueMacro)
                bridge_to_legacy(unified_macros, literal_const, "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register literal value macros: {e}")
            
        # Set up access macros
        try:
            from macros.access_macros_di import AccessMacro
            # Internal access operations
            access_ops = ["67lang:access_field", "67lang:access_index", "67lang:access_local"]
            for access_op in access_ops:
                register_macro_manually(access_op, AccessMacro)
                bridge_to_legacy(unified_macros, access_op, "process")
                if access_op == "67lang:access_local":
                    bridge_to_legacy(unified_typecheck, access_op, "typecheck")
                    
            # High-level access aliases (a, an, access) with preprocessing
            access_aliases = ["a", "an", "access"]
            for access_alias in access_aliases:
                register_macro_manually(access_alias, AccessMacro, aliases=[])
                # These are handled entirely by preprocessing - no need to bridge process/typecheck
        except ImportError as e:
            raise RuntimeError(f"Failed to register access macros: {e}")
            
        # Set up call macro
        try:
            from macros.lang_call_macro_di import CallMacro
            register_macro_manually("67lang:call", CallMacro)
            bridge_to_legacy(unified_macros, "67lang:call", "process")
            bridge_to_legacy(unified_typecheck, "67lang:call", "typecheck")
        except ImportError as e:
            raise RuntimeError(f"Failed to register call macro: {e}")
            
        # Set up scope macros
        try:
            from macros.scope_macro_di import ScopeMacro
            scope_macro_names = ["do", "then", "else", "67lang:file"]
            for scope_name in scope_macro_names:
                register_macro_manually(scope_name, ScopeMacro)
                bridge_to_legacy(unified_macros, scope_name, "process")
                if scope_name in ["do", "67lang:file"]:
                    bridge_to_legacy(unified_typecheck, scope_name, "typecheck")
        except ImportError as e:
            raise RuntimeError(f"Failed to register scope macros: {e}")
            
        # Set up noscope macro
        try:
            from macros.noscope_macro_di import NoscopeMacro
            register_macro_manually("noscope", NoscopeMacro)
            bridge_to_legacy(unified_macros, "noscope", "process")
        except ImportError as e:
            raise RuntimeError(f"Failed to register noscope macro: {e}")

    def get_new_ident(self, name: str | None):
        ident = f"_{hex(self.incremental_id)}"
        if name:
            ident += f"_{to_valid_js_ident(name)}"
        self.incremental_id += 1
        return ident

    def get_metadata(self, node: Node, metadata_type: type):
        """Get metadata for a node, auto-computing Macro and Args if missing"""
        node_id = id(node)
        default_logger.log("metadata", f"get metadata {str(metadata_type)} for {node_id} {node.content}")
        
        # Auto-compute Macro and Args if not present

        # TODO. why. why does that need to be commented out. this doesn't make any sense. explain. i beg you explain.
        if metadata_type in [Macro, Args]: # and (node_id not in self._node_metadata or metadata_type not in self._node_metadata[node_id]):
            self._ensure_macro_args_computed(node)
        
        if node_id in self._node_metadata and metadata_type in self._node_metadata[node_id]:
            return self._node_metadata[node_id][metadata_type]
        
        # Check if there's a default factory from the old TypeMap system
        from utils import TypeMap
        if metadata_type in TypeMap._default_factories:
            value = TypeMap._default_factories[metadata_type]()
            self.set_metadata(node, metadata_type, value)
            return value
        
        raise KeyError(f"No metadata of type {metadata_type} for node")

    def maybe_metadata(self, node: Node, metadata_type: type):
        """Get metadata for a node if it exists, return None otherwise"""
        try:
            return self.get_metadata(node, metadata_type)
        except KeyError:
            return None

    def set_metadata(self, node: Node, metadata_type: type, value: Any):
        """Set metadata for a node"""
        node_id = id(node)
        if node_id not in self._node_metadata:
            self._node_metadata[node_id] = {}
        self._node_metadata[node_id][metadata_type] = value
        default_logger.log("metadata", f"set metadata {str(metadata_type)} {str(value)} for {id(node)} {node.content}")

    def invalidate_metadata(self, node: Node):
        """Invalidate metadata for a node and all its descendants when tree changes"""
        node_id = id(node)
        if node_id in self._node_metadata:
            del self._node_metadata[node_id]
        
        # Recursively invalidate children
        for child in node.children:
            self.invalidate_metadata(child)

    def _ensure_macro_args_computed(self, node: Node):
        """Ensure Macro and Args metadata is computed for a node"""
        from node import Macro, Args
        from strutil import cut
        
        macro, args = cut(node.content, " ")
        self.set_metadata(node, Macro, macro)
        self.set_metadata(node, Args, args)

    def register(self, node: Node):
        self.nodes.append(node)

    def assert_(self, must_be_true: bool, node: Node, message: str, error_type: str = None):
        if not must_be_true:
            from error_types import ErrorType
            if error_type is None:
                error_type = ErrorType.ASSERTION_FAILED
            self.compile_error(node, f"failed to assert: {message}", error_type)
            raise MacroAssertFailed(message)

    def compile_error(self, node: Node, error: str, error_type: str):
        """Add a compile error with explicit error type."""
        pos = node.pos or Position(0, 0)
        entry: dict[str, Any] = { # TODO dataclass
            "recoverable": False, # TODO
            "line": pos.line,
            "char": pos.char,
            "content": node.content,
            "error": error,
            "error_type": error_type
        }
        self.compile_errors.append(entry)

    def compile(self):
        # Discover macros first
        with default_logger.indent("compile", "discovering macros"):
            for node in self.nodes:
                self.__discover_macros(node)
            
        solution_node = self.make_node("67lang:solution", Position(0, 0), self.nodes or [])
            
        # Execute the processing pipeline
        for step in self.processing_steps:
            step_name = step.__class__.__name__
            with default_logger.indent("compile", f"processing step: {step_name}"):
                ctx = MacroContext(
                    statement_out=StringIO(),  # dummy for non-emission steps
                    expression_out=StringIO(),
                    node=solution_node,
                    compiler=self,
                    current_step=step,
                )
                step.process_node(ctx)
        
        if len(self.compile_errors) != 0:
            return "" # TODO - raise an error instead ?
        
        return self._js_output

    def __discover_macros(self, node: Node):
        # TODO lstring macros should perhaps get special handling here...
        self._ensure_macro_args_computed(node)
        for child in node.children:
            self.__discover_macros(child)

    def make_node(self, content: str, pos: Position, children: None | list[Node]) -> Node:
        n = Node(content, pos, children)
        self.__discover_macros(n)
        return n

    # TODO - probably time to nuke this one...
    def compile_fn_call(self, ctx: MacroContext, call: str, nodes: Sequence[Node], ident:bool=True):
        from dataclasses import replace
        args: list[str] = []
        for child in nodes:
            expression_out = IndentedStringIO()
            child_ctx = replace(ctx, node=child, expression_out=expression_out)
            child_ctx.current_step.process_node(child_ctx)
            expression_out = expression_out.getvalue()
            if expression_out:
                args.append(expression_out)
            
        ident_value = ""
        if ident:
            ident_value = ctx.compiler.get_new_ident(call)
            ctx.statement_out.write(f"const {ident_value} = ")
        ctx.statement_out.write(f"{call}")
        joiner = Joiner(ctx.statement_out, ", ")
        for i in args:
            with joiner:
                ctx.statement_out.write(i)
        ctx.statement_out.write(")\n")
        if ident:
            ctx.expression_out.write(ident_value)

    @property
    def safely(self):
        @contextmanager
        def _safely():
            try:
                yield
            except MacroAssertFailed:
                pass
        return _safely()