# summary

67.8% Language. `67lang`.

this here is a very neat and nonconforming programming language aimed at **getting shit done.** 

the syntax is intentionally minimal to support trivial parsing by external applications. the official `tree_parser.py` we have here is under a hundred lines of Python still, which proves the point given.

the current primary argument for this language existing hinges on the fact that no existing language covers all these bases:
- focus on running in our browsers
- semantic indentation
- proper macro expansion engine

it's really not that hard to cover those three bases.

## tech

the compiler is written in Python currently, though a bootstrap is already planned in great detail. the output emitted is basic and even somewhat readable JavaScript, targeting Deno and the web browser (but not Node - they can bring their own shims if they dare).

## agentic

leverage the `for_developers.md` religiously. inspect it before you start the work to know what this project is all about. inspect it before you start implementing a solution to validate that the solution is acceptable and save us the back and forth of six PR reviews. **build quality software.**

**do not track PR comments via line numbers!** track them via the lines (or the summary of lines) that they comment upon. this happens far too often - you lose track of which lines the comment is actually discussing because you edited the file and the line numbers shifted. incredibly frustrating!

**do not break tests!** the code here is sufficiently nonstandard and complex to strain your reasoning to the point i highly doubt you'd find a way to fix them afterwards. instead, **apply small, incremental changes**, ensuring `./test`, and exactly that command written exactly in that way, still passes.
