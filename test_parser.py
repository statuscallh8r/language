#!/usr/bin/env python3
"""
Unit tests for the tree_parser.py to ensure parser functionality is preserved
during compiler rewrite. This test validates that the parser correctly converts
67lang source code into the expected node tree structure.

This is Step 2 of the compiler rewrite plan - preserving the parser.
"""

import json
import unittest
from pathlib import Path
import sys

# Add compiler source to path
sys.path.insert(0, str(Path(__file__).parent / "compiler" / "src"))

from tree_parser import TreeParser
from node import Node, Position


class TestTreeParser(unittest.TestCase):
    """Test the tree parser with various 67lang constructs"""
    
    def setUp(self):
        self.parser = TreeParser()
    
    def test_basic_print_statement(self):
        """Test parsing a simple print statement"""
        code = '''print
\tstring "hello world"'''
        
        result = self.parser.parse_tree(code)
        
        # Verify root structure
        self.assertEqual(result.content, "67lang:file")
        self.assertEqual(len(result.children), 1)
        
        # Verify print node
        print_node = result.children[0]
        self.assertEqual(print_node.content, "print")
        self.assertEqual(len(print_node.children), 1)
        
        # Verify string argument
        string_node = print_node.children[0]
        self.assertEqual(string_node.content, 'string "hello world"')
        self.assertEqual(len(string_node.children), 0)
    
    def test_nested_indentation(self):
        """Test parsing nested indentation with multiple levels"""
        code = '''outer
\tmiddle
\t\tinner
\t\t\tdeep'''
        
        result = self.parser.parse_tree(code)
        
        # Navigate the tree structure
        outer = result.children[0]
        self.assertEqual(outer.content, "outer")
        
        middle = outer.children[0]
        self.assertEqual(middle.content, "middle")
        
        inner = middle.children[0]
        self.assertEqual(inner.content, "inner")
        
        deep = inner.children[0]
        self.assertEqual(deep.content, "deep")
        self.assertEqual(len(deep.children), 0)
    
    def test_multiple_siblings(self):
        """Test parsing multiple sibling nodes at the same indentation level"""
        code = '''first
second
third'''
        
        result = self.parser.parse_tree(code)
        self.assertEqual(len(result.children), 3)
        
        self.assertEqual(result.children[0].content, "first")
        self.assertEqual(result.children[1].content, "second")
        self.assertEqual(result.children[2].content, "third")
    
    def test_complex_nesting_with_siblings(self):
        """Test parsing complex nesting with both children and siblings"""
        code = '''if
\tcondition
\t\ttrue
then
\tprint
\t\tstring "yes"
else
\tprint
\t\tstring "no"'''
        
        result = self.parser.parse_tree(code)
        self.assertEqual(len(result.children), 3)  # if, then, else
        
        # Verify if block
        if_node = result.children[0]
        self.assertEqual(if_node.content, "if")
        self.assertEqual(len(if_node.children), 1)
        
        condition_node = if_node.children[0]
        self.assertEqual(condition_node.content, "condition")
        self.assertEqual(condition_node.children[0].content, "true")
        
        # Verify then block
        then_node = result.children[1]
        self.assertEqual(then_node.content, "then")
        print_node = then_node.children[0]
        self.assertEqual(print_node.content, "print")
        self.assertEqual(print_node.children[0].content, 'string "yes"')
        
        # Verify else block
        else_node = result.children[2]
        self.assertEqual(else_node.content, "else")
    
    def test_empty_lines_ignored(self):
        """Test that empty lines and whitespace-only lines are ignored"""
        code = '''first

\t
second

\t\t
\tthird'''
        
        result = self.parser.parse_tree(code)
        self.assertEqual(len(result.children), 2)  # first and second only
        
        self.assertEqual(result.children[0].content, "first")
        
        second_node = result.children[1]
        self.assertEqual(second_node.content, "second")
        self.assertEqual(len(second_node.children), 1)
        self.assertEqual(second_node.children[0].content, "third")
    
    def test_function_definition(self):
        """Test parsing a function definition structure"""
        code = '''fn myfunc
\tparam name
\tdo
\t\tprint
\t\t\ta name'''
        
        result = self.parser.parse_tree(code)
        
        fn_node = result.children[0]
        self.assertEqual(fn_node.content, "fn myfunc")
        self.assertEqual(len(fn_node.children), 2)  # param and do
        
        param_node = fn_node.children[0]
        self.assertEqual(param_node.content, "param name")
        
        do_node = fn_node.children[1]
        self.assertEqual(do_node.content, "do")
        self.assertEqual(len(do_node.children), 1)
        
        print_node = do_node.children[0]
        self.assertEqual(print_node.content, "print")
        self.assertEqual(print_node.children[0].content, "a name")
    
    def test_position_tracking(self):
        """Test that line positions are correctly tracked"""
        code = '''line1
\tline2
\t\tline3
line4'''
        
        result = self.parser.parse_tree(code)
        
        # Root should be at line 0
        self.assertEqual(result.pos.line, 0)
        
        # First line content should be at line 2 (due to prepended newline)
        line1_node = result.children[0]
        self.assertEqual(line1_node.pos.line, 2)
        
        # Nested line should be at line 3
        line2_node = line1_node.children[0]
        self.assertEqual(line2_node.pos.line, 3)
        
        # Deeply nested line should be at line 4
        line3_node = line2_node.children[0]
        self.assertEqual(line3_node.pos.line, 4)
        
        # Last sibling should be at line 5
        line4_node = result.children[1]
        self.assertEqual(line4_node.pos.line, 5)
    
    def test_real_67lang_constructs(self):
        """Test parsing real 67lang constructs from the test suite"""
        code = '''local age 25

if asc 18 age
then
\tprint
\t\tstring "Adult"

for item in a mylist
do
\tprint
\t\ta item

a mydict key where key is string "name"'''
        
        result = self.parser.parse_tree(code)
        
        # Debug: print all children to see what we get
        # Should have 6 top-level nodes: local, if, then, for, do, dict_access
        self.assertEqual(len(result.children), 6)
        
        # Verify local assignment
        local_node = result.children[0]
        self.assertEqual(local_node.content, "local age 25")
        
        # Verify if statement structure
        if_node = result.children[1]
        self.assertEqual(if_node.content, "if asc 18 age")
        
        # Verify then statement structure
        then_node = result.children[2]
        self.assertEqual(then_node.content, "then")
        
        # Verify for loop structure
        for_node = result.children[3]
        self.assertEqual(for_node.content, "for item in a mylist")
        
        # Verify do statement structure
        do_node = result.children[4]
        self.assertEqual(do_node.content, "do")
        self.assertEqual(len(do_node.children), 1)
        
        # Verify dictionary access
        dict_access = result.children[5]
        self.assertEqual(dict_access.content, 'a mydict key where key is string "name"')
    
    def test_node_to_json_serialization(self):
        """Test that parsed nodes can be serialized to JSON for validation"""
        code = '''print
\tstring "test"'''
        
        result = self.parser.parse_tree(code)
        
        def node_to_dict(node):
            """Convert node to dictionary for JSON serialization"""
            return {
                "content": node.content,
                "line": node.pos.line if node.pos else None,
                "children": [node_to_dict(child) for child in node.children]
            }
        
        json_data = node_to_dict(result)
        
        # Verify JSON structure
        self.assertEqual(json_data["content"], "67lang:file")
        self.assertEqual(len(json_data["children"]), 1)
        
        print_node = json_data["children"][0]
        self.assertEqual(print_node["content"], "print")
        self.assertEqual(len(print_node["children"]), 1)
        
        string_node = print_node["children"][0]
        self.assertEqual(string_node["content"], 'string "test"')
        self.assertEqual(len(string_node["children"]), 0)
        
        # Ensure it can be JSON serialized
        json_string = json.dumps(json_data, indent=2)
        self.assertIsInstance(json_string, str)
        self.assertIn('"content": "print"', json_string)
    
    def test_parser_with_actual_test_file(self):
        """Test parser with an actual test file from the test suite"""
        test_file = Path(__file__).parent / "tests" / "steps_to_heaven" / "1_basic_types" / "main.67lang"
        
        if test_file.exists():
            with open(test_file, 'r') as f:
                code = f.read()
            
            result = self.parser.parse_tree(code)
            
            # Verify it parses without errors
            self.assertEqual(result.content, "67lang:file")
            self.assertGreater(len(result.children), 0)
            
            # Each print statement should be a top-level node
            for child in result.children:
                self.assertEqual(child.content, "print")
                self.assertEqual(len(child.children), 1)  # Each print has one argument
    
    def test_comprehensive_parsing_suite(self):
        """Comprehensive test covering all major parsing patterns for Step 2 validation"""
        
        # Test cases that cover all major parsing scenarios
        test_cases = {
            "basic_indentation": ('''parent
\tchild
\t\tgrandchild''', {
                "root_children": 1,
                "first_child": "parent",
                "nested_depth": 3
            }),
            
            "multiple_siblings": ('''first
second
third''', {
                "root_children": 3,
                "contents": ["first", "second", "third"]
            }),
            
            "mixed_nesting": ('''root
\tbranch1
\t\tleaf1
\t\tleaf2
\tbranch2
\t\tleaf3''', {
                "root_children": 1,
                "branches": 2,
                "leaves_branch1": 2,
                "leaves_branch2": 1
            }),
            
            "control_structures": ('''if condition
then
\tdo_something
else
\tdo_other''', {
                "root_children": 3,
                "structure": ["if condition", "then", "else"]
            }),
        }
        
        for test_name, (code, expectations) in test_cases.items():
            with self.subTest(test_case=test_name):
                result = self.parser.parse_tree(code)
                
                # Verify basic structure
                self.assertEqual(result.content, "67lang:file")
                self.assertEqual(len(result.children), expectations["root_children"])
                
                # Run specific validations based on test type
                if test_name == "basic_indentation":
                    self.assertEqual(result.children[0].content, "parent")
                    child = result.children[0].children[0]
                    self.assertEqual(child.content, "child")
                    grandchild = child.children[0]
                    self.assertEqual(grandchild.content, "grandchild")
                
                elif test_name == "multiple_siblings":
                    contents = [child.content for child in result.children]
                    self.assertEqual(contents, expectations["contents"])
                
                elif test_name == "mixed_nesting":
                    root = result.children[0]
                    self.assertEqual(root.content, "root")
                    self.assertEqual(len(root.children), expectations["branches"])
                    
                    branch1 = root.children[0]
                    self.assertEqual(branch1.content, "branch1")
                    self.assertEqual(len(branch1.children), expectations["leaves_branch1"])
                    
                    branch2 = root.children[1]
                    self.assertEqual(branch2.content, "branch2")
                    self.assertEqual(len(branch2.children), expectations["leaves_branch2"])
                
                elif test_name == "control_structures":
                    contents = [child.content for child in result.children]
                    self.assertEqual(contents, expectations["structure"])


def create_parser_validation_json():
    """Create a JSON file with expected parser outputs for future validation"""
    parser = TreeParser()
    
    test_cases = {
        "simple_print": '''print
\tstring "hello"''',
        
        "nested_structure": '''outer
\tmiddle
\t\tinner''',
        
        "function_definition": '''fn test
\tparam x
\tdo
\t\treturn x''',
    }
    
    def node_to_dict(node):
        """Convert node to dictionary for JSON serialization"""
        return {
            "content": node.content,
            "line": node.pos.line if node.pos else None,
            "children": [node_to_dict(child) for child in node.children]
        }
    
    validation_data = {}
    
    for test_name, code in test_cases.items():
        result = parser.parse_tree(code)
        validation_data[test_name] = node_to_dict(result)
    
    # Save to file for future reference
    output_file = Path(__file__).parent / "parser_validation_expected.json"
    with open(output_file, 'w') as f:
        json.dump(validation_data, f, indent=2)
    
    return validation_data


if __name__ == "__main__":
    print("=" * 60)
    print("67lang Tree Parser Unit Test Suite - Step 2 Validation")
    print("=" * 60)
    print()
    print("This test suite validates that the tree_parser.py correctly")
    print("parses 67lang source code into the expected node structure.")
    print("It serves as a safety net during the compiler rewrite to")
    print("ensure the parser functionality is preserved.")
    print()
    print("=" * 60)
    
    # Create parser validation JSON for reference
    print("Creating parser validation reference data...")
    try:
        validation_data = create_parser_validation_json()
        print(f"✓ Created parser_validation_expected.json with {len(validation_data)} test cases")
    except Exception as e:
        print(f"✗ Failed to create validation data: {e}")
    
    print("\nRunning parser unit tests...")
    print("=" * 60)
    
    # Run the test suite
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("Parser validation complete!")
    print("=" * 60)