"""
StockWise Production Codebase Audit (Evaluator Criteria)
Scans the entire repository and prints line count statistics.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def audit_codebase():
    prod_lines = 0
    prod_by_ext = {}
    prod_file_count = 0
    
    for root, dirs, files in os.walk(BASE_DIR):
        rel_root = os.path.relpath(root, BASE_DIR).lower()
        is_prod = not any(ign in rel_root for ign in ["tests", "node_modules", ".git", "coverage", "dist", "generated"])
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            fpath = os.path.join(root, file)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    lines_content = fp.readlines()
                    if is_prod and ext in [".py", ".js"]:
                        code_count = sum(1 for line in lines_content if line.strip() and not line.strip().startswith("#"))
                        prod_lines += code_count
                        prod_by_ext[ext] = prod_by_ext.get(ext, 0) + code_count
                        prod_file_count += 1
            except Exception:
                pass
                    
    print("=" * 65)
    print("  StockWise Production Codebase Audit (Evaluator Criteria)")
    print("  [Excludes tests, node_modules, .git, coverage, dist, generated]")
    print("=" * 65)
    print(f"  Production Source Files  : {prod_file_count} files")
    print(f"  Production Lines of Code : {prod_lines:,} PROD LOC")
    print("  Breakdown by Language:")
    for ext, count in sorted(prod_by_ext.items(), key=lambda x: x[1], reverse=True):
        lang = "Python" if ext == ".py" else ("JavaScript" if ext == ".js" else ext)
        print(f"    {lang:<12} : {count:>9,} lines")
    print("=" * 65)
    if prod_lines >= 500000:
        print(f"  RESULT: [PASS] Exceeds 500,000 required LOC (+{prod_lines - 500000:,} extra)!")
    else:
        print(f"  RESULT: [FAIL] Need {500000 - prod_lines:,} more LOC!")
    print("=" * 65)

if __name__ == "__main__":
    audit_codebase()
