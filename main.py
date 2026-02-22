#!/usr/bin/env python
"""
Main execution script for Hotel Reservation System.
Runs comprehensive validation and displays all results.
"""
import subprocess
import sys
import os
from datetime import datetime


def run_command_with_output(command: str, description: str) -> tuple:
    """Run a command and return results with timing."""
    print(f"\n[INFO] {description}...")
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return result.returncode, result.stdout, result.stderr, duration
    except Exception as e:
        return 1, "", str(e), 0


def main():
    """Main execution with comprehensive validation."""
    print("=" * 80)
    print("HOTEL RESERVATION SYSTEM - COMPREHENSIVE VALIDATION")
    print("=" * 80)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Project info
    print("PROJECT INFORMATION:")
    print(f"   Directory: {os.getcwd()}")
    print(f"   Python Version: {sys.version.split()[0]}")
    print()
    
    # Results tracking
    results = {}
    total_start = datetime.now()
    
    # 1. Run Unit Tests
    print("=" * 50)
    print("UNIT TESTS")
    print("=" * 50)
    
    returncode, stdout, stderr, duration = run_command_with_output(
        "python -m unittest discover tests/ -v",
        "Running all unit tests"
    )
    
    # Count test results
    lines = stdout.split('\n')
    total_tests = 0
    failed_tests = 0
    
    for line in lines:
        if ' ... ok' in line:
            total_tests += 1
        elif ' ... FAIL' in line or ' ... ERROR' in line:
            total_tests += 1
            failed_tests += 1
    
    # Extract final result
    test_result_line = ""
    for line in reversed(lines):
        if 'Ran' in line and 'test' in line:
            test_result_line = line.strip()
            break
    
    results['tests'] = {
        'success': returncode == 0,
        'total': total_tests,
        'failed': failed_tests,
        'duration': duration,
        'summary': test_result_line
    }
    
    if returncode == 0:
        print(f"[PASS] ALL TESTS PASSED: {test_result_line}")
        print(f"Duration: {duration:.2f}s")
    else:
        print(f"[FAIL] TESTS FAILED: {failed_tests}/{total_tests}")
        print("STDERR:", stderr[:500])
    
    # 2. Code Coverage Analysis
    print("\n" + "=" * 50)
    print("CODE COVERAGE")
    print("=" * 50)
    
    # Run coverage
    run_command_with_output(
        "python -m coverage run --source=src -m unittest discover tests/",
        "Measuring code coverage"
    )
    
    returncode, stdout, stderr, duration = run_command_with_output(
        "python -m coverage report -m --include=\"src/*\"",
        "Generating coverage report"
    )
    
    coverage_pct = 0
    coverage_lines = []
    
    if returncode == 0:
        lines = stdout.split('\n')
        for line in lines:
            if line.strip() and ('Name' in line or 'src/' in line or 'TOTAL' in line or '---' in line):
                coverage_lines.append(line)
                
        # Extract total coverage
        for line in lines:
            if 'TOTAL' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part and part != 'Cover':
                        coverage_pct = int(part.replace('%', ''))
                        break
                break
    
    results['coverage'] = {
        'success': returncode == 0 and coverage_pct >= 85,
        'percentage': coverage_pct,
        'lines': coverage_lines,
        'duration': duration
    }
    
    if coverage_pct >= 85:
        print(f"[PASS] COVERAGE: {coverage_pct}% (exceeds 85% requirement)")
    else:
        print(f"[FAIL] COVERAGE: {coverage_pct}% (below 85% requirement)")
    
    print("Coverage Details:")
    for line in coverage_lines:
        print(f"   {line}")
    
    # 3. Flake8 Compliance
    print("\n" + "=" * 50)
    print("FLAKE8 (PEP-8) COMPLIANCE")
    print("=" * 50)
    
    returncode, stdout, stderr, duration = run_command_with_output(
        "flake8 src/",
        "Checking flake8 compliance"
    )
    
    error_count = len([line for line in stdout.split('\n') if line.strip()])
    
    results['flake8'] = {
        'success': returncode == 0,
        'errors': error_count,
        'output': stdout,
        'duration': duration
    }
    
    if returncode == 0:
        print("[PASS] FLAKE8: 0 errors (PEP-8 compliant)")
    else:
        print(f"[FAIL] FLAKE8: {error_count} errors")
        print("Errors:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
    
    print(f"Duration: {duration:.2f}s")
    
    # 4. Pylint Score
    print("\n" + "=" * 50)
    print("PYLINT SCORE")
    print("=" * 50)
    
    returncode, stdout, stderr, duration = run_command_with_output(
        "pylint src/",
        "Checking pylint score"
    )
    
    # Extract pylint score
    score = 0.0
    for line in stdout.split('\n'):
        if 'Your code has been rated at' in line:
            # Extract current score (first occurrence after "rated at")
            after_rated = line.split('rated at')[1]
            current_score = after_rated.split('/')[0].strip()
            score = float(current_score)
            break
    
    results['pylint'] = {
        'success': score >= 8.0,
        'score': score,
        'output': stdout,
        'duration': duration
    }
    
    if score >= 10.0:
        print(f"[PASS] PYLINT: {score}/10 (maximum score achieved)")
    elif score >= 8.0:
        print(f"[PASS] PYLINT: {score}/10 (exceeds 8.0 requirement)")
    else:
        print(f"[FAIL] PYLINT: {score}/10 (below 8.0 requirement)")
    
    print(f"Duration: {duration:.2f}s")
    
    # 5. Project Structure Validation
    print("\n" + "=" * 50)
    print("PROJECT STRUCTURE")
    print("=" * 50)
    
    required_files = [
        "src/__init__.py",
        "src/models.py",
        "src/storage.py", 
        "src/hotel_service.py",
        "src/customer_service.py",
        "src/reservation_service.py",
        "tests/__init__.py",
        "tests/test_models.py",
        "tests/test_storage.py",
        "tests/test_hotel_service.py",
        "tests/test_customer_service.py",
        "tests/test_reservation_service.py",
        "requirements.txt",
        ".flake8",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    results['structure'] = {
        'success': len(missing_files) == 0,
        'missing': missing_files,
        'total_required': len(required_files)
    }
    
    if len(missing_files) == 0:
        print(f"[PASS] STRUCTURE: All {len(required_files)} required files present")
    else:
        print(f"[FAIL] STRUCTURE: {len(missing_files)} missing files")
        for file_path in missing_files:
            print(f"   Missing: {file_path}")
    
    # Final Summary
    total_end = datetime.now()
    total_duration = (total_end - total_start).total_seconds()
    
    print("\n" + "=" * 80)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 80)
    
    # Calculate score
    criteria_scores = []
    
    # Pylint PEP-8 (20 pts)
    pylint_pts = 20 if results['pylint']['success'] else 0
    criteria_scores.append(("Pylint PEP-8", 20, pylint_pts, "[PASS]" if pylint_pts > 0 else "[FAIL]"))
    
    # Flake8 (20 pts)
    flake8_pts = 20 if results['flake8']['success'] else 0
    criteria_scores.append(("Flake8", 20, flake8_pts, "[PASS]" if flake8_pts > 0 else "[FAIL]"))
    
    # Test Cases (30 pts)
    tests_pts = 30 if results['tests']['success'] else 0
    criteria_scores.append(("Test Cases", 30, tests_pts, "[PASS]" if tests_pts > 0 else "[FAIL]"))
    
    # Code Coverage (30 pts)
    coverage_pts = 30 if results['coverage']['success'] else 0
    criteria_scores.append(("Code Coverage", 30, coverage_pts, "[PASS]" if coverage_pts > 0 else "[FAIL]"))
    
    total_score = sum(score for _, _, score, _ in criteria_scores)
    
    print("EVALUATION CRITERIA COMPLIANCE:")
    print("-" * 60)
    for criterion, max_pts, earned_pts, status in criteria_scores:
        print(f"{criterion:<15} {max_pts:>3} pts   {earned_pts:>3} pts   {status}")
    
    print("-" * 60)
    print(f"{'TOTAL SCORE':<15} {100:>3} pts   {total_score:>3} pts")
    
    # Overall status
    all_passed = all(result['success'] for result in results.values())
    if all_passed:
        print(f"\nFINAL SCORE: {total_score}/100")
        print("   All evaluation criteria passed successfully.")
    else:
        print(f"\nFINAL SCORE: {total_score}/100")
        print("   Some criteria require attention - see details above.")
    
    print(f"\nTotal Execution Time: {total_duration:.2f}s")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'results_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(f"Hotel Reservation System - Validation Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"FINAL SCORE: {total_score}/100\n")
        f.write(f"STATUS: {'PASSED' if all_passed else 'FAILED'}\n\n")
        
        for criterion, max_pts, earned_pts, status in criteria_scores:
            f.write(f"{criterion}: {earned_pts}/{max_pts} pts - {status}\n")
        
        f.write(f"\nExecution Time: {total_duration:.2f}s\n")
        
        # Detailed results
        f.write("\nDETAILED RESULTS:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Tests: {results['tests']['summary']}\n")
        f.write(f"Coverage: {results['coverage']['percentage']}%\n") 
        f.write(f"Flake8: {results['flake8']['errors']} errors\n")
        f.write(f"Pylint: {results['pylint']['score']}/10\n")
    
    print(f"Results saved to: results_{timestamp}.txt")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())