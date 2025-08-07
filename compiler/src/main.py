#!/usr/bin/env python3

from io import StringIO
import json
from pathlib import Path
import argparse
import os
import sys
import traceback
from typing import Any, TextIO
from logger import configure_logger_from_args, default_logger

# Parse args first to configure logging before any macro registrations
parser = argparse.ArgumentParser()
parser.add_argument('input_dir')
parser.add_argument('output_file')
parser.add_argument('--errors-file', help="will output compilation errors and warnings (as JSON) into this file if specified")
parser.add_argument('--log', help="comma-separated list of log tags to enable (e.g., 'typecheck,macro'). omit to disable all logging.")
parser.add_argument('--expand', action='store_true', help="compile in two-step mode: .67lang → .67lang.expanded")
parser.add_argument('--rte', action='store_true', help="compile in two-step mode: .67lang.expanded → .js")

args = parser.parse_args()

# configure logging based on command line args BEFORE importing modules that register macros
configure_logger_from_args(args.log)

# Now import modules that register macros (these will respect the logging configuration)
from tree_parser import TreeParser
from macrocosm import Macrocosm

def human_readable(inspections: list[dict[str, Any]]) -> None:
    for i, entry in enumerate(reversed(inspections), 1):
        out = StringIO()
        print(f"\n\n{i}:")
        for k, v in entry.items():
            out.write(f"{k} = {v}\n")
        print(out.getvalue())

def write_json(inspections: list[dict[str, Any]], output: TextIO) -> None:
    json.dump(inspections, output, indent=2)
    output.write('\n')
    output.flush()



default_logger.compile("starting compilation process")
with default_logger.indent("compile", "initialization"):
    os.chdir(args.input_dir)
    rglob = "*.67lang.expanded" if args.rte else "*.67lang"
    result = list(Path(".").rglob("*.67lang"))
    default_logger.compile(f"found {len(result)} .67lang files: {[str(f) for f in result]}")
    its_just_macros = Macrocosm()
    
    # Log macro registry summary if registry logging is enabled
    from processor_base import unified_macros, unified_typecheck
    codegen_macros = ", ".join(unified_macros.all().keys())
    typecheck_macros = ", ".join(unified_typecheck.all().keys())
    default_logger.registry(f"macro registry initialized with codegen macros: {codegen_macros}")
    default_logger.registry(f"typecheck registry initialized with typecheck macros: {typecheck_macros}")  
    # Note: preprocessor macros are now encapsulated within PreprocessingStep

parser = TreeParser()
with default_logger.indent("compile", "parsing files"):
    for filename in result:
        default_logger.compile(f"parsing {filename}")
        with open(filename) as file:
            node = parser.parse_tree(file.read(), its_just_macros)
            its_just_macros.register(node)

crash = None
compiled = None

# Standard compilation: .67lang → (.js or .67lang.expanded)
with default_logger.indent("compile", "single-step compilation"):
    try:
        compiled = its_just_macros.compile()
    except Exception as e:
        exc_info = sys.exc_info()
        crash = ''.join(traceback.format_exception(*exc_info))
        default_logger.compile(f"compilation crashed: {e}")

if args.expand:
    # Write .67lang.expanded instead of .js
    # TODO - might need to think about this. might need to make this opt-in, it's useful
    #  to write out the expansion for debugging but it is very much an invalid expansion.
    #  oh! i know. wrap it in a `67lang.invalid_solution` which causes a compile error!
    default_logger.compile(f"expand mode: writing expanded form to {args.output_file}")
    with open(args.output_file, "w") as f:
        for node in its_just_macros.nodes:
            f.write(repr(node))
            f.write("\n\n")
else:
    # Write .js output
    if compiled:
        default_logger.compile(f"compilation successful, writing output to {args.output_file}")
        with open(args.output_file, "w") as f:
            f.write(compiled)

print("refactor confidently when the flame flickers.")

if len(its_just_macros.compile_errors) != 0 or crash:
    print(f"{len(its_just_macros.compile_errors)} compile errors.")
    if len(its_just_macros.compile_errors) != 0:
        if args.errors_file:
            with open(args.errors_file, 'w') as f:
                write_json(its_just_macros.compile_errors, f)
            print(f"seek them in {args.errors_file}.")
        else:
            human_readable(its_just_macros.compile_errors)
    
    if crash:
        print(crash, end='')
    
    exit(1)