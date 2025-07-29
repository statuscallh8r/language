# Simple Makefile for Indentifire development

# Variables
PYTHON = python3
DENO = .deno/bin/deno
COMPILER = compiler/src/main.py
TEST_RUNNER = test.py

# Colors for output
GREEN = \033[0;32m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help setup test test-compile clean install examples fizzbuzz

help: ## Show this help message
	@echo "$(BLUE)Indentifire Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Set up the development environment (install Deno, run tests)
	@echo "$(BLUE)Setting up Indentifire development environment...$(NC)"
	@./setup.sh

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(PYTHON) $(TEST_RUNNER)

test-compile: ## Run compilation tests only (faster)
	@echo "$(BLUE)Running compilation tests...$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(PYTHON) $(TEST_RUNNER) -c

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -name "*.js" -path "./test/*" -delete
	@find . -name ".ind.expanded" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf /tmp/indentifire_*

install: setup ## Install VSCode extensions for indentifire
	@echo "$(BLUE)Installing VSCode extensions...$(NC)"
	@./install-syntax.sh
	@./install-langserv.sh
	@echo "$(GREEN)VSCode extensions installed! Restart VSCode to activate.$(NC)"

# Example programs
examples: hello-world calculator fizzbuzz count-words anagram-groups ## Compile and run all example programs

fizzbuzz: ## Compile and run the FizzBuzz example
	@echo "$(BLUE)Compiling FizzBuzz example...$(NC)"
	@$(PYTHON) $(COMPILER) test/basics/fizzbuzz test/basics/fizzbuzz/out.js
	@echo "$(BLUE)Running FizzBuzz (3, 5, 15):$(NC)"
	@echo -e "3\n5\n15" | PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run test/basics/fizzbuzz/out.js

count-words: ## Compile and run the word counter example
	@echo "$(BLUE)Compiling word counter example...$(NC)"
	@$(PYTHON) $(COMPILER) test/basics/count_words test/basics/count_words/out.js
	@echo "$(BLUE)Running word counter:$(NC)"
	@echo "apple banana apple pear apple banana apple pear banana" | PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run test/basics/count_words/out.js

anagram-groups: ## Compile and run the anagram grouping example
	@echo "$(BLUE)Compiling anagram groups example...$(NC)"
	@$(PYTHON) $(COMPILER) test/basics/anagram_groups test/basics/anagram_groups/out.js
	@echo "$(BLUE)Running anagram groups:$(NC)"
	@echo "listen silent enlist tar rat banana" | PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run test/basics/anagram_groups/out.js

hello-world: ## Compile and run the hello world example
	@echo "$(BLUE)Compiling hello world example...$(NC)"
	@$(PYTHON) $(COMPILER) examples/hello_world examples/hello_world/hello.js
	@echo "$(BLUE)Running hello world:$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run examples/hello_world/hello.js

calculator: ## Compile and run the calculator example
	@echo "$(BLUE)Compiling calculator example...$(NC)"
	@$(PYTHON) $(COMPILER) examples/calculator examples/calculator/calc.js
	@echo "$(BLUE)Running calculator:$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run examples/calculator/calc.js

# Compilation helpers
compile-%: ## Compile a specific test (e.g., make compile-fizzbuzz)
	@echo "$(BLUE)Compiling $*...$(NC)"
	@$(PYTHON) $(COMPILER) test/basics/$* test/basics/$*/out.js

run-%: compile-% ## Compile and run a specific test (e.g., make run-fizzbuzz)
	@echo "$(BLUE)Running $*...$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(DENO) run test/basics/$*/out.js

# Development helpers
check: ## Check if the environment is set up correctly
	@echo "$(BLUE)Checking environment...$(NC)"
	@$(PYTHON) --version
	@if [ -f "$(DENO)" ]; then $(DENO) --version; else echo "$(RED)Deno not found. Run 'make setup' first.$(NC)"; fi
	@echo "$(GREEN)Environment check complete.$(NC)"

debug-%: ## Compile a test with debug output (e.g., make debug-fizzbuzz)
	@echo "$(BLUE)Compiling $* with debug output...$(NC)"
	@PATH="$(PWD)/.deno/bin:$$PATH" $(PYTHON) $(TEST_RUNNER) -g "*$*" -d