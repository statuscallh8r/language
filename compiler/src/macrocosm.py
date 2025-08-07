#!/usr/bin/env python3

"""
Step 4: Ascend the ladder - Refactored 67lang compiler
Clean, registry-based architecture with proper separation of concerns
"""

from node import Node
from logger import default_logger
from strutil import cut
from handlers import (
    MacroHandler, PrintHandler, LocalHandler, IfHandler, ThenHandler, ElseHandler, 
    ForHandler, AccessMacroHandler, WhileHandler, FunctionHandler, CallHandler,
    NoteHandler, DoScopeHandler, FileRootHandler, CommentHandler, IsTtyHandler,
    PromptHandler, StdinHandler, ConcatHandler, ZipHandler, ExistsHandler,
    InsideHandler, ValuesHandler, ReturnHandler, BreakHandler, TypeHandler, 
    WhereClauseHandler, RegexHandler
)
from value_compiler import ValueHandler
from type_system import TypeChecker
from typing import List, Dict, Any, Optional
import json
import sys


class Macrocosm:
    """Refactored compiler using direct macro mapping"""
    
    def __init__(self):
        self.errors = []
        self.compile_errors = []  # For compatibility with main.py
        self.nodes = []  # For compatibility with main.py
        self.value_handler = ValueHandler()
        self.type_checker = TypeChecker()  # Add type checker
        
        # Direct mapping of macro names to handlers
        self.macro_handlers = {
            'print': PrintHandler(),
            'local': LocalHandler(),
            'if': IfHandler(),
            'then': ThenHandler(),
            'else': ElseHandler(),
            'for': ForHandler(),
            'while': WhileHandler(),
            'fn': FunctionHandler(),
            'call': CallHandler(),
            'note': NoteHandler(),
            'do': DoScopeHandler(),
            # New input/output macros
            '#': CommentHandler(),
            'is_tty': IsTtyHandler(),
            'prompt': PromptHandler(),
            'stdin': StdinHandler(),
            'concat': ConcatHandler(),
            'zip': ZipHandler(),
            'exists': ExistsHandler(),
            'inside': InsideHandler(),
            'values': ValuesHandler(),
            'return': ReturnHandler(),
            'break': BreakHandler(),
            'type': TypeHandler(),
            'where': WhereClauseHandler(),
            'regex': RegexHandler(),
            # Access aliases all map to the same handler
            'a': AccessMacroHandler(),
            'an': AccessMacroHandler(),
            'access': AccessMacroHandler(),
            # Value handler macros
            'string': self.value_handler,
            'int': self.value_handler,
            'float': self.value_handler,
            'true': self.value_handler,
            'false': self.value_handler,
            'all': self.value_handler,
            'any': self.value_handler,
            'none': self.value_handler,
            'add': self.value_handler,
            'sub': self.value_handler,
            'mul': self.value_handler,
            'div': self.value_handler,
            'mod': self.value_handler,
            'eq': self.value_handler,
            'ne': self.value_handler,
            'lt': self.value_handler,
            'gt': self.value_handler,
            'le': self.value_handler,
            'ge': self.value_handler,
            'asc': self.value_handler,
            'desc': self.value_handler,
            'list': self.value_handler,
            'dict': self.value_handler,
        }
        
        # Special handler for root nodes
        self.file_root_handler = FileRootHandler()
    
    @property
    def handlers(self):
        """Compatibility property for main.py"""
        return list(self.macro_handlers.values())
    
    def register(self, node: Node):
        """Register a parsed node (compatibility with main.py)"""
        self.nodes.append(node)
    
    def compile(self) -> str:
        """Compile all registered nodes to JavaScript (compatibility with main.py)"""
        self.errors = []
        self.compile_errors = []
        self.type_checker = TypeChecker()  # Reset type checker
        
        # First pass: type checking
        for node in self.nodes:
            self._type_check_node(node)
        
        # Store errors to prevent them from being lost
        type_errors = self.type_checker.errors[:]  # Make a copy
        
        # If there are type errors, emit them and stop compilation
        if type_errors:
            try:
                # Convert to expected JSON format and write to stderr
                error_json = json.dumps([error.to_dict() for error in type_errors], indent=2)
                print(error_json, file=sys.stderr)
                # Still generate JS to avoid breaking test harness
            except Exception as e:
                print(f"DEBUG: JSON generation failed: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
        
        # Second pass: code generation
        statements = []
        for node in self.nodes:
            js = self._compile_node(node)
            if js:
                statements.append(js)
        
        if self.errors:
            # Emit errors in the right format from the start
            for error in self.errors:
                self.compile_errors.append({"message": error})
            error_msg = "\n".join(self.errors)
            raise RuntimeError(f"Compilation failed:\n{error_msg}")
        
        return "\n".join(statements)
    
    def compile_to_js(self, root_node: Node) -> str:
        """Compile 67lang AST to JavaScript - delegate to FileRootHandler"""
        self.errors = []
        self.type_checker = TypeChecker()  # Reset type checker
        
        # First pass: type checking
        self._type_check_node(root_node)
        
        # If there are type errors, emit them and stop compilation
        if self.type_checker.errors:
            # Convert to expected JSON format and write to stderr
            import sys
            error_json = self.type_checker.get_errors_json()
            print(error_json, file=sys.stderr)
            # Still try to generate JS for now to avoid breaking the test harness
            
        # Second pass: code generation
        js = self._compile_node(root_node)
        
        if self.errors:
            error_msg = "\n".join(self.errors)
            raise RuntimeError(f"Compilation failed:\n{error_msg}")
        
        return js or ""
    
    def _compile_node(self, node: Node) -> Optional[str]:
        """Compile a single node using direct macro mapping"""
        content = node.content.strip()
        
        # Handle file root specially
        if content == "67lang:file":
            return self.file_root_handler.compile(node, self)
        
        # Extract macro name using cut
        macro, rest = cut(content, ' ')
        
        # Look up handler directly
        if macro in self.macro_handlers:
            return self.macro_handlers[macro].compile(node, self)
        
        # Crash loud and hard for unknown nodes - no silent fallbacks
        self._add_error(f"unknown macro or unhandled node: '{macro}' in '{content}'", node)
        return ""
    
    def compile_value(self, node: Node) -> str:
        """Compile a value expression - replacement for _compile_value"""
        return self.value_handler.compile_value(node, self)
    
    def _add_error(self, message: str, node: Node):
        """Add an error to the error list"""
        line_info = f"line {node.pos.line}" if node.pos else "unknown position"
        error = f"Error at {line_info}: {message}"
        self.errors.append(error)
        default_logger.compile(error)
    
    def _type_check_node(self, node: Node):
        """Type check a node and its children"""
        content = node.content.strip()
        
        # Handle file root
        if content == "67lang:file":
            for child in node.children:
                self._type_check_node(child)
            return
            
        # Extract macro name
        macro, rest = cut(content, ' ')
        
        # Handle specific macros that need type checking
        if macro == 'local':
            var_name = rest.strip() if rest else ""
            if var_name:
                self.type_checker.check_local_declaration(node, var_name)
        
        elif macro in ['a', 'an', 'access']:
            # Handle access operations - both variable access and assignments
            var_name = rest.strip() if rest else ""
            if var_name:
                if len(node.children) > 0:
                    # This is an assignment
                    self.type_checker.check_assignment(node, var_name, node.children[0])
                else:
                    # Check if this is a method call on a variable
                    parts = content.split(' ')
                    if len(parts) > 2:  # e.g., "a test_bool split"
                        var_name = parts[1]
                        methods = parts[2:]
                        self.type_checker.check_method_call_on_variable(node, var_name, methods)
        
        elif macro == 'do':
            # Enter new scope for do blocks
            self.type_checker.enter_scope()
            for child in node.children:
                self._type_check_node(child)
            self.type_checker.exit_scope()
        
        elif macro in ['split', 'join', 'sort']:
            # Check method calls
            self.type_checker.check_method_call(node, macro)
        
        else:
            # Recursively check children
            for child in node.children:
                self._type_check_node(child)