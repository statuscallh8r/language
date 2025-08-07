# potential refactoring opportunities

collected during the circular dependency fix. items here are maintenance hazards that could slow down future development but aren't blocking current functionality.

## registry merge duplication in processor.py

**location**: `compiler/src/processor.py` lines 19-41

**issue**: manual registry merging with repetitive for-loops. this pattern appears 4 times with identical structure:

```python
for name, handler in some_registry.all().items():
    target_registry._registry[name] = handler
```

**maintenance hazard**: adding new macro modules requires manual updates to this merging code. easy to forget and creates fragile coupling between macro modules and the main processor.

**potential solution**: create a `merge_registries()` utility function or make MacroRegistry support `+=` operator for cleaner merging.

## circular import workarounds still present

**location**: `compiler/src/macros/access_macros.py` line 179

**issue**: still using local imports to avoid circular dependencies:

```python
# Import here to avoid circular imports
from steps.typecheck_step import TypeCheckingStep
```

**maintenance hazard**: this pattern could spread to other files. local imports are harder to track and understand.

**potential solution**: consider dependency injection or moving shared interfaces to a separate module.

## massive TODO count

**location**: throughout codebase (27 TODOs found)

**issue**: significant technical debt accumulation, particularly in:
- `macrocosm.py` (6 TODOs)
- `processor_base.py` (5 TODOs) 
- `access_macros.py` (3 TODOs)

**maintenance hazard**: TODOs without associated issues tend to accumulate and never get addressed. some indicate fundamental design issues.

**potential solution**: convert high-priority TODOs to actual GitHub issues with clear acceptance criteria.

## processor_base.py complexity

**location**: `compiler/src/processor_base.py` (300 lines)

**issue**: largest file in the codebase handling multiple responsibilities:
- macro context management
- builtin function definitions  
- prototype call handling
- error reporting

**maintenance hazard**: changes to any of these concerns require understanding the entire file. violates single responsibility principle.

**potential solution**: split into separate modules: `macro_context.py`, `builtins.py`, `prototype_calls.py`, `error_reporting.py`.

## hardcoded macro lists

**location**: `compiler/src/macros/comment_macros.py` line 22

**issue**: hardcoded list concatenation for macro registration:

```python
@code_linking.add(*(COMMENT_MACROS + ["string", "regex"])) # TODO - ugly. don't concat lists like that
```

**maintenance hazard**: adding new comment-like macros requires updating hardcoded lists in multiple places.

**potential solution**: use a more declarative registration system or macro inheritance.

## metadata access patterns

**location**: various files using `ctx.compiler.set_metadata()` and `ctx.compiler.get_metadata()`

**issue**: raw metadata access without type safety or validation.

**maintenance hazard**: typos in metadata keys won't be caught until runtime. difficult to track what metadata is used where.

**potential solution**: create typed metadata accessors or use dataclasses for metadata storage.

---

*this file should be updated whenever maintenance hazards are discovered during regular development work. items should be triaged periodically: fix immediately, create GitHub issue, or defer.*