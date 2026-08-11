import os
import subprocess
import sys
import glob

def run_tests():
    test_files = sorted(glob.glob("test_*.py"))
    # Exclude this file if it starts with test_ (but it starts with run_all_tests.py, so it's fine)
    
    passed = []
    failed = []
    timed_out = []
    
    print(f"Found {len(test_files)} test files to execute.")
    print("-" * 60)
    
    for test_file in test_files:
        print(f"Running {test_file}...", end="", flush=True)
        try:
            # Run with a 7-second timeout in case it opens a GUI or waits for input
            res = subprocess.run(
                [sys.executable, test_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=7,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            if res.returncode == 0:
                print(" [PASS]")
                passed.append(test_file)
            else:
                print(" [FAIL]")
                failed.append((test_file, res.returncode, res.stdout, res.stderr))
        except subprocess.TimeoutExpired as e:
            print(" [TIMEOUT]")
            # Try to grab stdout/stderr from the timeout exception if possible
            # Since text=True, stdout/stderr are strings or bytes depending on the exception. Let's make sure it handles both.
            def to_str(val):
                if isinstance(val, bytes):
                    return val.decode("utf-8", errors="ignore")
                return str(val) if val is not None else ""
            stdout = to_str(e.stdout)
            stderr = to_str(e.stderr)
            timed_out.append((test_file, stdout, stderr))
            
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total: {len(test_files)}")
    print(f"Passed: {len(passed)} / {len(test_files)}")
    print(f"Failed: {len(failed)} / {len(test_files)}")
    print(f"Timed out: {len(timed_out)} / {len(test_files)}")
    print("-" * 60)
    
    if passed:
        print("\nPASSED TESTS:")
        for p in passed:
            print(f"  - {p}")
            
    if failed:
        print("\nFAILED TESTS:")
        for f_name, code, stdout, stderr in failed:
            print(f"  - {f_name} (Exit code: {code})")
            # Print a snippet of stderr
            err_lines = [line for line in stderr.splitlines() if line.strip()]
            if err_lines:
                print("    Last error line:", err_lines[-1])
            else:
                out_lines = [line for line in stdout.splitlines() if line.strip()]
                if out_lines:
                    print("    Last stdout line:", out_lines[-1])
                    
    if timed_out:
        print("\nTIMED OUT TESTS (Possibly GUI or interactive):")
        for t_name, stdout, stderr in timed_out:
            print(f"  - {t_name}")
            
if __name__ == "__main__":
    run_tests()
