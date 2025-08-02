# discovering 67lang: a programming language that actually gives a damn

*an outsider's exploration of a refreshingly uncompromising language project*

## stumbling upon something different

i was browsing github when i stumbled across a repository called "language" with the tagline "a better programming language. the ones *you* made? all suck. this one? **doesn't.**" 

now, that's either the most arrogant thing i've ever read, or someone who's genuinely confident they've built something worth paying attention to. the blunt honesty was refreshing in a world of corporate-speak and "innovative solutions." so naturally, i had to dig deeper.

what i found was 67lang (apparently "67.8% Language" - love the specificity), a programming language that seems to have been built by someone who got fed up with the status quo and decided to just... build better tools.

## first impressions: this ain't your typical language repo

most programming language repositories follow a predictable pattern: lengthy readme with feature lists, extensive documentation, maybe some marketing copy about "blazing fast" performance. 67lang's readme is different:

```
# what

a better programming language. the ones *you* made? all suck. this one? **doesn't.**

key features:
- targets the most powerful and contributed and researched and optimized runtime (V8)
- actual semantic indentation?!
- (planned) custom macro expansion

# how

`./test.py` is the main entrypoint for you, at least for now.

# license

i will open source it all later, i haven't decided on the right license just yet
```

no bullshit. no venture capital buzzwords. just "here's what it does, here's how to try it." the test suite *is* the documentation, which is either lazy or brilliant - i'm leaning toward brilliant.

## syntax that makes you think

let's look at some actual code. here's fizzbuzz in 67lang:

```67lang
local fizz_divisor
local buzz_divisor
local n

if
    is_tty
then
    access fizz_divisor
        prompt
            string "fizz? "
else
    local input
        stdin
    
    access input
        access input split
            string "\n"
    
    a fizz_divisor
        an input key
            where key is
                int 0

local i
    int 0
while
    asc
        access i
        access n
do
    local out
        string ""
    
    if
        eq
            mod
                access i
                access fizz_divisor
            int 0
    then
        access out
            concat
                access out
                string "fizz"
    
    print
        access out
```

at first glance, this looks... verbose. where are the parentheses? the semicolons? the curly braces? but then something clicks. 

the indentation isn't just stylistic - it's semantic. every level of indentation represents a level of nesting or argument passing. `access fizz_divisor` followed by an indented `prompt` means "call the prompt method on fizz_divisor." it's like method chaining, but vertical.

what really got me was this pattern:
```67lang
a fizz_divisor
    an input key
        where key is
            int 0
```

this translates to `fizz_divisor = input[0]` in most languages, but look at how readable it is. "assign to fizz_divisor an input key where key is int 0." it reads like english.

## the philosophy: correctness over convenience

digging into the compiler source (written in python, about 1800 lines total), i found something interesting in their style guide:

> defensive programming! you wrote `if "=" in pair`, great! but what `if not "=" in pair`? things are rarely optional around here. crash loud, crash hard, crash fast, scream harsh.

and

> **the tests are our spec.** no matter what you may find elsewhere, unless it is discoverable via the `./test.py`, it has no say as to what the language syntax or semantics are.

this isn't a language designed by committee or built to appease corporate sponsors. it's built by someone who cares about building correct, reliable software. the compiler doesn't emit warnings - only errors you can recover from and crashes you cannot.

there's no backwards compatibility yet because "for whom? the language is barely usable as of now." instead of maintaining compatibility with a moving target, they just... fix the tests when they break something.

## method chaining that doesn't suck

one of the most elegant features is the method chaining syntax. consider this example from their tests:

```67lang
local key
    a word split sort join
        where split takes
            string ""
        where join takes
            string ""
```

this chains `split("")`, `sort()`, and `join("")` on `word`. in javascript, you'd write:
```javascript
let key = word.split("").sort().join("");
```

but the 67lang version is self-documenting. you can see exactly which arguments go to which methods. no more hunting through nested parentheses to figure out what's calling what.

## field access that makes sense

dictionary/object access is handled beautifully:

```67lang
a person key
    where key is
        string "name"
    string "bob"
```

this sets `person["name"] = "bob"`. but you're not limited to calling it "key" - you can use any identifier:

```67lang
a person data_we_would_like_to_store
    where data_we_would_like_to_store is
        string "age"
    int 30
```

the syntax is "forever flexible" as they put it. it's the same underlying operation, but the code can express intent more clearly.

## compilation that just works

the compiler is surprisingly straightforward. it parses the semantic indentation into a tree, applies macro expansions, does type checking, and emits readable javascript. here's what that fizzbuzz example compiles to:

```javascript
let fizz_divisor = globalThis._67lang.store();
let buzz_divisor = globalThis._67lang.store();
let n = globalThis._67lang.store();

if (globalThis.Deno?.isatty(globalThis.Deno.stdin.rid)) {
    fizz_divisor(globalThis.prompt("fizz? "));
    buzz_divisor(globalThis.prompt("buzz? "));
    n(globalThis.prompt("n? "));
} else {
    let input = globalThis._67lang.stdin();
    input(input().split("\n"));
    fizz_divisor(input()[0]);
    buzz_divisor(input()[1]);
    n(input()[2]);
}
// ... rest of the logic
```

it's not the most optimized javascript you'll see, but it's readable and it works. the compiler prioritizes correctness and clarity over micro-optimizations.

## type checking that means business

the language includes a type system that's still work-in-progress, but already shows promise:

```67lang
local typed_number
    type int
    int 42

local typed_string
    type str
    string "hello"

# this will fail compilation:
must_compile_error FIELD_TYPE_MISMATCH=336
    local bad_assignment
        type str  
        a typed_number
```

the `must_compile_error` macro is genius - it documents expected failures right in the source code and validates that the type checker catches them.

## what's actually here vs. what's planned

currently working:
- semantic indentation parsing
- compilation to javascript/deno
- basic type checking
- method chaining
- control flow (if/then/else, for/do, while/do)
- built-in functions (print, eq, add, concat, etc.)
- field access with flexible syntax
- string operations including regex
- list and dictionary support

still planned:
- full macro expansion system
- stricter type checking
- custom syntax support
- infinitely extensible macroprocessor
- the ability to "redefine if" (whatever that means)

## the interesting technical bits

the tree parser is allegedly under 100 lines of python and "proves the point" about trivial parsing enabling external codegen. looking at the source, it's actually quite elegant - it uses semantic indentation to build a tree structure without needing complex grammar rules.

the macro system is where things get interesting. they have different types of macros:
- literal macros (for basic data types)
- preprocessing macros (for syntax transformations)  
- typecheck macros (for type system integration)

the architecture suggests they're building toward something much more ambitious - a language where users can extend not just the standard library, but the syntax and semantics themselves.

## why this matters

most programming languages are designed by academics, committees, or corporations. they optimize for different things - academic rigor, design-by-committee consensus, or market adoption.

67lang feels different. it's designed by someone who actually builds software and got frustrated with existing tools. the documentation literally says "made not to sell but to be actually useful" and "made not for you" - it's refreshingly honest about its priorities.

the semantic indentation isn't just a gimmick - it makes the code structure visible at a glance. the flexible field access syntax lets you write code that reads like documentation. the type system crashes hard on errors instead of trying to be helpful.

## rough edges and limitations

this is still early-stage software. the compiler is 1800 lines of python, which is impressive for what it accomplishes, but also suggests there's a lot of work left to do.

the javascript output isn't optimized - everything goes through a runtime library. performance-sensitive applications might struggle.

there's no package management, no standard library beyond basics, no ide integration beyond syntax highlighting. you can build a web server with it (they claim), but you'd be building a lot of infrastructure yourself.

the type system is work-in-progress. some tests are expected to fail compilation, which suggests the type checker isn't complete.

and honestly? the attitude might turn some people off. the "your languages suck, mine doesn't" approach is either endearing or obnoxious depending on your perspective.

## the bigger picture

what struck me most about 67lang isn't any individual feature - it's the coherence of vision. every design decision seems to stem from a consistent philosophy: make the structure of code visible, crash on errors instead of hiding them, prioritize correctness over convenience.

the semantic indentation isn't just about avoiding curly braces - it makes the tree structure of the code explicit. the flexible syntax isn't just about being different - it lets you write code that expresses intent clearly. the strict error handling isn't just about being pedantic - it prevents bugs from hiding.

there's something refreshing about a language project that says "we're going to do this right, even if it's different" instead of "we're going to be compatible with everything else, even if it's wrong."

## should you try it?

if you're building production systems, probably not yet. this is still experimental software with a lot of rough edges.

but if you're curious about language design, or frustrated with the compromises in existing languages, or just want to see what semantic indentation actually looks like in practice? absolutely.

the entire test suite runs in under 2 seconds. you can have it compiled and running examples in minutes. and the examples in the test directory are genuinely instructive - they show off the language features without getting bogged down in hello-world banality.

## final thoughts

67lang reminds me why i got excited about programming in the first place. it's not trying to be the next big thing or disrupt the enterprise market. it's just someone who cares about building good tools trying to build better ones.

the author notes "our greatest enemy is our indifference" at the bottom of the readme. in a world of languages designed by marketing departments and committees, 67lang feels like it comes from someone who still gives a damn about the craft.

whether it succeeds or not, it's worth paying attention to. at minimum, it's a fascinating exploration of what programming languages could be if we threw out all our assumptions and started fresh.

and honestly? after spending time with the codebase, i'm rooting for it.

## try it yourself

```bash
git clone https://github.com/statuscallh8r/language
cd language
./test.py
```

all the examples are in the `tests/` directory. start with `tests/language_documentation/main.67lang` for a comprehensive tour, or `tests/basics/fizzbuzz/main.67lang` for something familiar.

the compiler will either work perfectly or crash spectacularly. either way, you'll learn something about what's possible when someone builds a language they actually want to use.

---

*this exploration was based on the state of the repository as of january 2025. the language is still evolving rapidly, so features and syntax may have changed by the time you read this.*