#!/usr/bin/env python3

from io import StringIO
import json
from pathlib import Path
import argparse
import os
import sys
import traceback
from typing import Any, TextIO
from tree_parser import TreeParser
from processor import Compiler

def human_readable(inspections: list[dict[str, Any]]) -> None:
    for i, entry in enumerate(reversed(inspections), 1):
        out = StringIO()
        print(f"\n\n{i}:")
        for k, v in entry.items():
            out.write(f"{k} = {v}")
        print(out.getvalue())

def write_json(inspections: list[dict[str, Any]], output: TextIO) -> None:
    json.dump(inspections, output, indent=2)
    output.write('\n')
    output.flush()

parser = argparse.ArgumentParser()
parser.add_argument('input_dir')
parser.add_argument('output_file')
parser.add_argument('--errors-file', help="will output compilation errors and warnings (as JSON) into this file if specified")

args = parser.parse_args()

os.chdir(args.input_dir)
result = list(Path(".").rglob("*.ind"))
compiler = Compiler()

parser = TreeParser()
for filename in result:
    with open(filename) as file:
        node = parser.parse_tree(file.read())
        compiler.register(node)

crash = None
compiled = None
try:
    compiled = compiler.compile()
except Exception as e:
    exc_info = sys.exc_info()
    crash = ''.join(traceback.format_exception(*exc_info))

if compiled:
    # Ensure the output directory exists
    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_file, "w") as f:
        f.write(compiled)
else:
    print("No compiled output generated")

expanded_file = Path(args.output_file).parent / ".ind.expanded"
print(f"expanded into {expanded_file}")

# Ensure the directory exists before writing
expanded_file.parent.mkdir(parents=True, exist_ok=True)

with open(expanded_file, "w") as f:
    for node in compiler.nodes:
        f.write(repr(node))
        f.write("\n\n")
print("refactor confidently when the flame flickers.")

if len(compiler.compile_errors) != 0 or crash:
    if len(compiler.compile_errors) != 0:
        if args.errors_file:
            with open(args.errors_file, 'w') as f:
                write_json(compiler.compile_errors, f)
        else:
            human_readable(compiler.compile_errors)
    
    if crash:
        print(crash, end='')
    
    exit(1)