#!/usr/bin/env python3
"""
test that validates gitignore behavior for test artifacts.
mentioned in issue #15 as a "test to ./test which would then invoke another specific test 
within ./test and assert that it generates the right artifacts and they actually are visible to git"
"""

import subprocess
import sys
from pathlib import Path
import tempfile

def run_command(cmd, cwd=None):
    """run a command and return returncode, stdout, stderr"""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def main():
    repo_root = Path(__file__).parent
    
    print("testing gitignore behavior for test artifacts...")
    
    # run a specific test to generate artifacts
    print("running test to generate artifacts...")
    returncode, stdout, stderr = run_command(
        ["python3", "test", "--compile", "--glob", "anagra"], 
        cwd=repo_root
    )
    
    if returncode != 0:
        print(f"ERROR: test failed with code {returncode}")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return False
    
    test_dir = repo_root / "tests" / "basics" / "anagram_groups"
    
    # check that valuable artifacts exist
    valuable_artifacts = [
        test_dir / ".67lang.expanded",  # macro expansion history
        test_dir / "out.js",            # JS emission history
        test_dir / "success.stdout",    # test behavior history
        test_dir / "main.67lang",       # source code
    ]
    
    print("checking that valuable artifacts exist...")
    for artifact in valuable_artifacts:
        if not artifact.exists():
            print(f"ERROR: valuable artifact missing: {artifact}")
            return False
        print(f"✓ {artifact.name}")
    
    # check git status to ensure temporary files are ignored
    print("checking git status...")
    returncode, stdout, stderr = run_command(
        ["git", "status", "--porcelain", str(test_dir)], 
        cwd=repo_root
    )
    
    if returncode != 0:
        print(f"ERROR: git status failed: {stderr}")
        return False
    
    status_lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    
    # should not see any test_diffs/ or .actual files in git status
    for line in status_lines:
        if "test_diffs" in line:
            print(f"ERROR: test_diffs should be ignored by git: {line}")
            return False
        if ".actual" in line:
            print(f"ERROR: .actual files should be ignored by git: {line}")
            return False
    
    print("✓ no temporary files in git status")
    
    # verify test_diffs directory exists but is ignored
    test_diffs_dir = test_dir / "test_diffs"
    if test_diffs_dir.exists():
        print("checking that test_diffs directory is ignored...")
        returncode, stdout, stderr = run_command(
            ["git", "check-ignore", str(test_diffs_dir)], 
            cwd=repo_root
        )
        if returncode != 0:
            print(f"ERROR: test_diffs directory should be ignored by git")
            return False
        print("✓ test_diffs directory is properly ignored")
    
    # check that .67lang.expanded files are properly tracked
    print("checking .67lang.expanded file tracking...")
    expanded_file = test_dir / ".67lang.expanded"
    if expanded_file.exists():
        returncode, stdout, stderr = run_command(
            ["git", "ls-files", str(expanded_file)], 
            cwd=repo_root
        )
        if returncode != 0:
            print(f"ERROR: git ls-files failed: {stderr}")
            return False
        if not stdout.strip():
            print(f"ERROR: .67lang.expanded file should be tracked: {expanded_file}")
            return False
        print("✓ .67lang.expanded file is properly tracked")
    
    print("all gitignore behavior tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)