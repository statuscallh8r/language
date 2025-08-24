# bootstrapping strategy

## hybrid migration approach

JSON bridge enables temporary coexistence - Python processes JSON, .ind processes JSON. compiler pipeline clean of ephemeral metadata makes this practical.

1. **coexistence** - both compilers operational
2. **component replacement** - migrate modules one by one  
3. **continuous validation** - test compatibility throughout
4. **cutover** - complete transition to self-hosted

### pipeline evolution
```
current:  .ind → python parser → python macros → python types → python js → .js
target:   .ind → lang parser → lang macros → lang types → lang js → .js

phase 1:  .ind → lang parser → python macros → python types → python js → .js  
phase 2:  .ind → lang parser → lang macros → python types → python js → .js
phase 3:  .ind → lang parser → lang macros → lang types → python js → .js
phase 4:  .ind → lang parser → lang macros → lang types → lang js → .js
```

## data structures

### ast representation (using design decision)
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

starts with dictionary approach, evolves to struct-based classes

### error handling (using design decision)
try/catch macros mapping directly to JS try/catch:
```
try
	parse_tree
		a invalid_source
catch error
	print
		concat
			string "parsing failed: "
			a error message
```

## development approach

### validation strategy
- continuous integration by running `./test.py` on each PR  
- configure `./test.py` to run each test with both old Python compiler and new hybrid
- rollback on >0% test failures
- same error messages and locations required for test compatibility

**success metric:** compiler fully rewritten in .ind with all existing tests passing