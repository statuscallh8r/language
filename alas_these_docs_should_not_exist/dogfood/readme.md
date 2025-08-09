# dogfood roadmap

this directory contains the technical analysis and roadmap for bootstrapping this programming language - rewriting the entire Python-based compiler in the language itself.

## what's in here

- `current_state.md` - comprehensive analysis of what the language can do right now
- `gaps_analysis.md` - detailed breakdown of what's missing for self-hosting  
- `roadmap.md` - phased development plan to get from here to bootstrapped
- `bootstrapping_strategy.md` - technical approach and architecture decisions
- `open_questions.md` - design decisions that need answers from the maintainer

## context

the current compiler is written in Python (~2094 lines) and works well, but Python's lack of macro support and general verbosity makes it painful to extend. the goal is to eat our own dogfood and prove the language is capable of serious development work.

## testing philosophy

all existing tests (currently 13) must continue to pass throughout the bootstrapping process. the new compiler should be a drop-in replacement that generates identical or equivalent JavaScript output.