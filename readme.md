# Indentifire 🔥

A better programming language with semantic indentation, strict type checking, and JavaScript compilation.

**It's not snake oil, it's here now.** The tests compile and run. You could build a webserver in it already if you so chose.

## Key Features

- **Targets V8/Deno** - Compiles to JavaScript and runs on the most powerful and optimized runtime
- **Semantic Indentation** - Like Python/YAML, but for a systems programming language  
- **Strict Type Checking** - Catch errors at compile time with the strictest type system
- **Clean Syntax** - Readable without tedious punctuation overload
- **Monadic Field Access** - Expressive method chaining for data manipulation
- **Trivial Parsing** - Simple enough for external codegen and tooling

**Planned Features:**
- Custom macro expansion system
- Infinitely extensible macroprocessor with alternate backends  
- Custom syntax support
- Ability to redefine core language constructs

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/statuscallh8r/language.git
cd language

# Set up the development environment (installs Deno automatically)
./setup.sh

# Or use make
make setup
```

### Your First Program

Create a file `hello.ind`:

```indentifire
do
    print
        string "Hello, World!"
    
    local name
        prompt
            string "What's your name? "
    
    print
        concat
            string "Hello, "
            name
            string "!"
```

Compile and run:

```bash
# Compile to JavaScript
python3 compiler/src/main.py . hello.js

# Run with Deno
deno run hello.js

# Or use make shortcuts
make compile-hello
make run-hello
```

## Language Syntax

Indentifire uses semantic indentation where the structure of your code determines the program flow.

### Basic Structure

```indentifire
# This is a comment using a string statement
string "Comments are just strings in statement context"

# Variable declaration and assignment
local variable_name
    initial_value

# Access (read/modify) variables  
access variable_name
    new_value

# Function calls and method chaining
result
    some_function
        argument1
        argument2

# Conditional execution
if
    condition
then
    action_if_true
else  
    action_if_false

# Loops
while
    condition
do
    loop_body
```

### Data Types

```indentifire
# Integers
local count
    int 42

# Strings  
local message
    string "Hello"

# String with custom delimiters (avoid escaping)
local path
    string /home/user/file.txt/

# Boolean
local flag
    bool true

# Lists are created through operations
local words
    access input split
        string " "
```

### Method Chaining

```indentifire
# Powerful data pipeline operations
result
    access input split
        string "\n"
    access previous sort
    access previous join
        string ", "
```

## Examples

The `examples/` directory contains sample programs:

- **Hello World** - Basic I/O and string operations
- **Calculator** - Arithmetic with error handling  
- **FizzBuzz** - Classic programming problem
- **Word Counter** - Text processing and data structures
- **Anagram Groups** - String manipulation and algorithms

Run examples:

```bash
make examples        # Run all examples
make fizzbuzz       # Run specific example
make hello-world    # Run hello world
```

## Development

### Running Tests

```bash
make test           # Run all tests
make test-compile   # Run compilation tests only (faster)
```

### Building Programs

```bash
# Compile any .ind file
python3 compiler/src/main.py <input_directory> <output_file.js>

# Run the compiled JavaScript
deno run <output_file.js>
```

### IDE Support

Install VSCode extensions for syntax highlighting and language server:

```bash
make install        # Installs both extensions
```

Or manually:

```bash
./install-syntax.sh    # Syntax highlighting
./install-langserv.sh  # Language server
```

### Development Commands

```bash
make help           # Show all available commands
make check          # Verify environment setup
make clean          # Clean generated files
make debug-fizzbuzz # Compile with debug output
```

## Project Structure

```
├── compiler/           # Indentifire compiler (Python)
│   └── src/           # Compiler source code
├── examples/          # Example programs
├── test/              # Test suite
│   ├── basics/        # Basic language feature tests
│   └── fail_typechecks/ # Type checking failure tests
├── langserv/          # VSCode language server
├── highlight/         # VSCode syntax highlighting
├── setup.sh           # Development environment setup
├── Makefile           # Development commands
└── test.py            # Test runner
```

## Requirements

- **Python 3.9+** - For the compiler
- **Deno** - For running compiled JavaScript (installed automatically by setup.sh)

No external Python dependencies required - uses only the standard library.

## Contributing

This project is in active development. The core language features work, but there's always room for improvement in:

- Documentation and tutorials
- Standard library expansion  
- IDE tooling enhancements
- Performance optimizations
- Language feature additions

## License

All Rights Reserved. Copyright (c) 2025 status.call.h8r

*Note: The author plans to open source this later with an appropriate license.*

---

**Made not to sell but to be actually useful. Made not for you. Developed by somebody who actually cares.**

*Our greatest enemy is our indifference.*
