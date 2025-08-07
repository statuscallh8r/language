#!/usr/bin/env python3

"""
Type system for 67lang compiler
Handles type checking, inference, and error reporting
"""

from node import Node, Position
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
import sys


class TypeKind(Enum):
    """Basic type kinds in 67lang"""
    INT = "int"
    STR = "str" 
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    NONE = "None"
    UNKNOWN = "unknown"


class TypeInfo:
    """Information about a type"""
    
    def __init__(self, kind: TypeKind, element_type: Optional['TypeInfo'] = None):
        self.kind = kind
        self.element_type = element_type  # For lists, dicts etc
    
    def __str__(self):
        if self.element_type:
            return f"{self.kind.value}[{self.element_type}]"
        return self.kind.value
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return self.kind == other.kind and self.element_type == other.element_type


class TypeErrorKind(Enum):
    """Types of type checking errors"""
    FIELD_TYPE_MISMATCH = "FIELD_TYPE_MISMATCH"
    MISSING_TYPE = "MISSING_TYPE"
    ARGUMENT_TYPE_MISMATCH = "ARGUMENT_TYPE_MISMATCH"
    UNKNOWN_VARIABLE = "UNKNOWN_VARIABLE"


class TypeError:
    """A type checking error"""
    
    def __init__(self, kind: TypeErrorKind, message: str, node: Node, content: str = None):
        self.kind = kind
        self.message = message
        self.node = node
        self.content = content or node.content
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "recoverable": False,
            "line": self.node.pos.line if self.node.pos else 0,
            "char": self.node.pos.char if self.node.pos else 0,
            "content": self.content,
            "error": self.message,
            "error_type": self.kind.value
        }


class Scope:
    """A variable scope for type checking"""
    
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.variables: Dict[str, TypeInfo] = {}
        self.declared_types: Dict[str, TypeInfo] = {}  # Variables with explicit type declarations
    
    def declare_variable(self, name: str, var_type: TypeInfo, declared: bool = False):
        """Declare a variable with a type"""
        self.variables[name] = var_type
        if declared:
            self.declared_types[name] = var_type
    
    def get_variable_type(self, name: str) -> Optional[TypeInfo]:
        """Get the type of a variable"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable_type(name)
        return None
    
    def get_declared_type(self, name: str) -> Optional[TypeInfo]:
        """Get the declared type of a variable (if explicitly typed)"""
        if name in self.declared_types:
            return self.declared_types[name]
        elif self.parent:
            return self.parent.get_declared_type(name)
        return None
    
    def update_variable_type(self, name: str, var_type: TypeInfo):
        """Update the type of an existing variable"""
        if name in self.variables:
            self.variables[name] = var_type
        elif self.parent:
            self.parent.update_variable_type(name, var_type)


class TypeChecker:
    """Type checker for 67lang"""
    
    def __init__(self):
        self.current_scope = Scope()
        self.errors: List[TypeError] = []
        
        # Built-in method signatures
        self.method_signatures = {
            'split': {'input': TypeKind.STR, 'output': TypeKind.LIST},
            'join': {'input': TypeKind.LIST, 'output': TypeKind.STR},
            'sort': {'input': TypeKind.LIST, 'output': TypeKind.LIST},
        }
    
    def enter_scope(self) -> Scope:
        """Enter a new scope"""
        self.current_scope = Scope(self.current_scope)
        return self.current_scope
    
    def exit_scope(self):
        """Exit the current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def add_error(self, kind: TypeErrorKind, message: str, node: Node, content: str = None):
        """Add a type error"""
        # Add "failed to assert: " prefix to match expected format
        full_message = f"failed to assert: {message}"
        error = TypeError(kind, full_message, node, content)
        self.errors.append(error)
    
    def infer_type(self, node: Node) -> TypeInfo:
        """Infer the type of an expression"""
        content = node.content.strip()
        
        # Literal types
        if content.startswith('int '):
            return TypeInfo(TypeKind.INT)
        elif content.startswith('string '):
            return TypeInfo(TypeKind.STR)
        elif content.startswith('float '):
            return TypeInfo(TypeKind.INT)  # For now, treat as int 
        elif content in ['true', 'false']:
            return TypeInfo(TypeKind.BOOL)
        elif content.startswith('list'):
            return TypeInfo(TypeKind.LIST)
        elif content.startswith('dict'):
            return TypeInfo(TypeKind.DICT)
            
        # Variable access - handle simple variable names
        if content.startswith('a ') or content.startswith('an ') or content.startswith('access '):
            parts = content.split(' ')
            if len(parts) >= 2:
                var_name = parts[1]
                # Look for method chaining
                if len(parts) > 2:
                    # This is a method chain like 'a test_str split sort join'
                    var_type = self.current_scope.get_variable_type(var_name)
                    if var_type:
                        return self.infer_method_chain_type_for_var(var_type, parts[2:])
                    else:
                        self.add_error(TypeErrorKind.UNKNOWN_VARIABLE, 
                                     f"unknown variable: {var_name}", node)
                        return TypeInfo(TypeKind.UNKNOWN)
                else:
                    # Simple variable access
                    var_type = self.current_scope.get_variable_type(var_name)
                    if var_type:
                        return var_type
                    else:
                        # For debugging, let's see what variables are available
                        all_vars = []
                        scope = self.current_scope
                        while scope:
                            all_vars.extend(scope.variables.keys())
                            scope = scope.parent
                        self.add_error(TypeErrorKind.UNKNOWN_VARIABLE, 
                                     f"unknown variable: {var_name} (available: {', '.join(all_vars)})", node)
                        return TypeInfo(TypeKind.UNKNOWN)
        
        return TypeInfo(TypeKind.UNKNOWN)
    
    def infer_method_chain_type_for_var(self, start_type: TypeInfo, methods: list[str]) -> TypeInfo:
        """Infer the type of a method chain starting from a known variable type"""
        current_type = start_type
        
        for method in methods:
            if method in self.method_signatures:
                sig = self.method_signatures[method]
                expected_input = TypeKind(sig['input'])
                if current_type.kind == expected_input:
                    current_type = TypeInfo(TypeKind(sig['output']))
                else:
                    # Type mismatch in method chain
                    self.add_error(TypeErrorKind.ARGUMENT_TYPE_MISMATCH,
                                 f"argument demands {sig['input']} and is given {current_type.kind.value}",
                                 # Use a dummy node position for now - this is a limitation
                                 Node("", Position(0, 0), []), f"67lang:call {method}")
                    return TypeInfo(TypeKind.UNKNOWN)
        
        return current_type
    
    def check_local_declaration(self, node: Node, var_name: str) -> Optional[TypeInfo]:
        """Check a local variable declaration"""
        
        declared_type = None
        actual_type = None
        
        # Look for type declaration in children
        type_child = None
        value_child = None
        
        for child in node.children:
            child_content = child.content.strip()
            if child_content.startswith('type '):
                type_child = child
            elif not child_content.startswith('#'):  # Ignore comments
                value_child = child
        
        # Get declared type
        if type_child:
            type_content = type_child.content.strip()
            type_name = type_content.split(' ', 1)[1] if ' ' in type_content else ''
            if type_name in ['int', 'str', 'bool', 'list', 'dict']:
                declared_type = TypeInfo(TypeKind(type_name))
        
        # Get actual type from value
        if value_child:
            actual_type = self.infer_type(value_child)
        else:
            # No initial value provided
            if declared_type:
                self.add_error(TypeErrorKind.MISSING_TYPE,
                             f"field demands {declared_type.kind.value} but is given None",
                             node, f"local {var_name}")
                # Still register the variable with its declared type
                self.current_scope.declare_variable(var_name, declared_type, True)
                return declared_type
            else:
                actual_type = TypeInfo(TypeKind.NONE)
        
        # Check type compatibility
        if declared_type and actual_type and declared_type.kind != actual_type.kind:
            if actual_type.kind != TypeKind.UNKNOWN:  # Don't report error for unknown types
                self.add_error(TypeErrorKind.FIELD_TYPE_MISMATCH,
                             f"field demands {declared_type.kind.value} but is given {actual_type.kind.value}",
                             node, f"local {var_name}")
        
        # Register the variable - always register with declared type if available
        # This allows later operations to know what type was declared
        final_type = declared_type if declared_type else actual_type
        if final_type:
            self.current_scope.declare_variable(var_name, final_type, declared_type is not None)
        
        return final_type
    
    def check_assignment(self, node: Node, var_name: str, value_node: Node):
        """Check variable assignment"""
        declared_type = self.current_scope.get_declared_type(var_name)
        actual_type = self.infer_type(value_node)
        
        if declared_type and actual_type and declared_type.kind != actual_type.kind:
            if actual_type.kind != TypeKind.UNKNOWN:
                self.add_error(TypeErrorKind.FIELD_TYPE_MISMATCH,
                             f"field demands {declared_type.kind.value} but is given {actual_type.kind.value}",
                             node, f"67lang:access_local {var_name}")
        
        # Update variable type
        if actual_type:
            self.current_scope.update_variable_type(var_name, actual_type)
    
    def check_method_call_on_variable(self, node: Node, var_name: str, methods: list[str]):
        """Check a method call on a variable like 'a test_bool split'"""
        var_type = self.current_scope.get_variable_type(var_name)
        if not var_type:
            self.add_error(TypeErrorKind.UNKNOWN_VARIABLE,
                         f"unknown variable: {var_name}", node)
            return
        
        current_type = var_type
        for method in methods:
            if method in self.method_signatures:
                sig = self.method_signatures[method]
                expected_input = TypeKind(sig['input'])
                if current_type.kind == expected_input:
                    current_type = TypeInfo(TypeKind(sig['output']))
                else:
                    # Type mismatch in method call
                    self.add_error(TypeErrorKind.ARGUMENT_TYPE_MISMATCH,
                                 f"argument demands {sig['input']} and is given {current_type.kind.value}",
                                 node, f"67lang:call {method}")
                    return
    
    def check_method_call(self, node: Node, method_name: str):
        """Check a method call for type compatibility - legacy method"""
        # This is kept for compatibility but the new check_method_call_on_variable is preferred
        pass
    
    def get_errors_json(self) -> str:
        """Get errors as JSON string"""
        error_dicts = [error.to_dict() for error in self.errors]
        return json.dumps(error_dicts, indent=2)