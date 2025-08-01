# bootstrapping roadmap

# bootstrapping roadmap

## prerequisite language features

before beginning any compiler rewrite, implement missing syntax needed for practical development:

### classes and structs (1-2 days)
- **struct/class syntax** - user-defined types with fields
- **multimethod dispatch** - polymorphic behavior
- **approach:** struct-based syntax as decided

### file I/O and module system (1-2 days)  
- **file operations** - read_file, write_file, list_files via Deno APIs
- **import mechanism** - enforced alphabetical ordering for compiler  
- **approach:** simple alphabetic hack initially

### enhanced stdlib (1-2 days)
- **WebIDL auto-generation** - leverage entire Deno standard library
- **string processing, json, collections** - expose JS implementations
- **approach:** thin wrappers around Deno APIs

## hybrid compiler development

once language is sufficiently powerful, begin systematic rewrite:

### phase 1: parser rewrite (days 1-3)
- **tree_parser.ind** - reimplement `tree_parser.py` in language
- **JSON bridge** - communicate via subprocess and JSON serialization  
- **testing:** `./test.py` runs with both parsers, identical results

### phase 2: macro system (days 4-7)
- **macro_registry.ind** - macro registration and processing
- **approach:** builtin macros can be Turing complete, userspace macros remain declarative
- **testing:** full integration with all existing tests passing

### phase 3: type checker (days 8-12)
- **type_checker.ind** - static type validation system  
- **features:** generics and unions for compiler robustness
- **testing:** identical type errors and messages as Python version

### phase 4: code generation (days 13-16)
- **js_emitter.ind** - JavaScript output generation
- **testing:** all existing tests pass (exact JS output not required)

## success criteria

- compiler fully rewritten in .ind files
- all 13 existing tests pass with hybrid/self-hosted compiler  
- same error messages and locations as Python version
- continuous integration approach throughout - no separate "integration phase"

