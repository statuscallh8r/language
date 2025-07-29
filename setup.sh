#!/bin/bash

# Indentifire Development Environment Setup Script
# This script sets up everything needed to compile and run indentifire programs

set -e

echo "🔥 Setting up Indentifire development environment..."

# Check Python version
echo "📋 Checking Python installation..."
python3 --version || {
    echo "❌ Python 3 is required but not found. Please install Python 3.9 or later."
    exit 1
}

# Extract Python version numbers
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or later is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if Deno is already installed and accessible
echo "📋 Checking Deno installation..."
if command -v deno >/dev/null 2>&1; then
    echo "✅ Deno $(deno --version | head -1) found in PATH"
elif [ -f ".deno/bin/deno" ]; then
    echo "✅ Local Deno installation found"
    export PATH="$PWD/.deno/bin:$PATH"
else
    echo "📥 Installing Deno locally..."
    
    # Create directory for local Deno installation
    mkdir -p .deno/bin
    
    # Download and install Deno
    case "$(uname -s)" in
        Linux*)
            DENO_URL="https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip"
            ;;
        Darwin*)
            if [ "$(uname -m)" = "arm64" ]; then
                DENO_URL="https://github.com/denoland/deno/releases/latest/download/deno-aarch64-apple-darwin.zip"
            else
                DENO_URL="https://github.com/denoland/deno/releases/latest/download/deno-x86_64-apple-darwin.zip"
            fi
            ;;
        *)
            echo "❌ Unsupported operating system: $(uname -s)"
            echo "Please install Deno manually from https://deno.land/manual/getting_started/installation"
            exit 1
            ;;
    esac
    
    echo "  Downloading Deno from $DENO_URL..."
    if command -v curl >/dev/null 2>&1; then
        curl -L "$DENO_URL" -o /tmp/deno.zip
    elif command -v wget >/dev/null 2>&1; then
        wget -O /tmp/deno.zip "$DENO_URL"
    else
        echo "❌ Neither curl nor wget found. Please install one of them or install Deno manually."
        exit 1
    fi
    
    echo "  Extracting Deno..."
    (cd /tmp && unzip -q deno.zip && mv deno "$OLDPWD/.deno/bin/")
    chmod +x .deno/bin/deno
    rm -f /tmp/deno.zip
    
    # Add to PATH for this session
    export PATH="$PWD/.deno/bin:$PATH"
    
    echo "✅ Deno installed successfully"
fi

# Verify the installation by running tests
echo "🧪 Running test suite to verify installation..."
if python3 test.py; then
    echo ""
    echo "🎉 Setup complete! Indentifire is ready to use."
    echo ""
    echo "📚 Next steps:"
    echo "  1. Try compiling an example: python3 compiler/src/main.py test/basics/fizzbuzz test/basics/fizzbuzz/out.js"
    echo "  2. Run the compiled program: .deno/bin/deno run test/basics/fizzbuzz/out.js"
    echo "  3. Read the getting started guide in the README"
    echo ""
    echo "💡 Add .deno/bin to your PATH to use deno directly:"
    echo "  export PATH=\"\$PWD/.deno/bin:\$PATH\""
else
    echo "❌ Setup verification failed. Please check the error messages above."
    exit 1
fi