# gaps analysis

## critical missing features for self-hosting

### 1. file system operations
- read/write files, directory traversal, path manipulation
- **current:** stdin only, no file I/O
- **impact:** can't read .ind files or write .js output

### 2. module system and imports  
- import mechanism, module resolution, namespaces
- **current:** single file only, no code reuse
- **impact:** can't organize compiler into modules
- **approach:** use current system with enforced alphabetical ordering

### 3. error handling
- try/catch mechanisms, exception handling
- **current:** errors crash programs
- **approach:** try/catch macros mapping to JS try/catch

### 4. better string manipulation
- regex, formatting, parsing utilities
- **current:** basic split/concat only
- **approach:** leverage Deno standard library via WebIDL

### 5. process execution
- external commands, environment variables
- **current:** no subprocess capability
- **approach:** use Deno's built-in process APIs

### 6. data structures and types
- custom types, AST representation
- **current:** primitives and dicts only
- **approach:** struct-based syntax with multimethod dispatch

## standard library gaps

### file operations
```
read_file(path), write_file(path, content), file_exists(path)
list_dir(path), path_join(parts...), path_dirname(path)
```

### string utilities  
```
format_string(template, args...), regex_match(pattern, text)
string_escape(text), trim(text), pad_left/right(text, length)
```

### json/data handling
```
json_parse(text), json_stringify(object), parse_int(text)
```

## compiler-specific needs

### ast representation
**approach:** struct-based classes with fields
```
class Node
	field content
		type str
	field position
		type Position  
	field children
		type list
			self.class
```

### type system
**focus:** correctness over performance, generics and unions needed
- support advanced features for compiler robustness
- expressiveness over performance trade-offs

### macro system  
**approach:** purely declarative macros only
- no imperative/Turing complete macros
- all compiled, no runtime expansion
- add new macro types as needed

### memory management
**approach:** rely on Deno/JavaScript GC
- no manual memory management
- JavaScript performance sufficient for compiler needs

## development strategy

**priority order:**
1. file I/O and basic utilities (critical path)
2. module system with enforced ordering
3. error handling via try/catch macros  
4. standard library leveraging Deno APIs
5. advanced type features and optimizations

**success criteria:** compiler fully rewritten in .ind with all existing tests passing