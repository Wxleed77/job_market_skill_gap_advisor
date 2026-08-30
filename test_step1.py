"""
STEP 1 Test: Display normalized output from seed dataset.
"""

import json
from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings

def test_step1():
    """Test STEP 1: seed dataset + normalization."""
    
    print("=" * 80)
    print("STEP 1: Seed Dataset + Normalization")
    print("=" * 80)
    print(f"\nTotal raw postings in seed data: {len(RAW_POSTINGS)}\n")
    
    # Normalize all postings
    normalized = normalize_postings(RAW_POSTINGS)
    
    print(f"Successfully normalized: {len(normalized)} postings\n")
    
    # Show 3 sample postings
    sample_indices = [0, 9, 19]  # First, middle, last
    
    for idx in sample_indices:
        posting = normalized[idx]
        print("-" * 80)
        print(f"Sample {idx + 1}:")
        print(json.dumps(posting, indent=2, default=str))
        print()
    
    print("=" * 80)
    print("\nSummary Statistics:")
    print(f"  Total postings normalized: {len(normalized)}")
    print(f"  Cities represented: {len(set(p['city'] for p in normalized))}")
    print(f"  Role categories: {sorted(set(p['role_category'] for p in normalized))}")
    print(f"  Sources: {sorted(set(p['source'] for p in normalized))}")
    print(f"  Date range: {min(p['date_posted'] for p in normalized)} to {max(p['date_posted'] for p in normalized)}")
    
    # Skill frequency
    all_skills = []
    for p in normalized:
        all_skills.extend(p['skills_extracted'])
    
    from collections import Counter
    skill_counts = Counter(all_skills)
    print(f"\n  Top 10 skills across all postings:")
    for skill, count in skill_counts.most_common(10):
        print(f"    - {skill}: {count} postings")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_step1()
