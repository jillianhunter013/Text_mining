#!/usr/bin/env python3
"""
FALLBACK: Generate synthetic news data if CC-News download fails.

This creates realistic-looking data with the same structure as CC-News.
Use only if the real data download is broken.

Usage:
    uv run python scripts/generate_synthetic_data.py
"""

import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

# Configuration
TARGET_SIZE_GB = 16
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "cc_news_large.csv"

# Realistic-ish content
DOMAINS = [
    "reuters.com", "nytimes.com", "bbc.com", "cnn.com", "washingtonpost.com",
    "theguardian.com", "apnews.com", "bloomberg.com", "wsj.com", "ft.com",
    "politico.com", "thehill.com", "axios.com", "vice.com", "vox.com",
    "npr.org", "latimes.com", "chicagotribune.com", "usatoday.com", "time.com"
]

TOPICS = [
    "economy", "politics", "technology", "climate", "health", "business",
    "science", "sports", "entertainment", "world", "finance", "education"
]

WORDS = [
    "the", "and", "of", "to", "in", "a", "is", "that", "for", "it", "with",
    "as", "was", "on", "are", "be", "by", "at", "this", "have", "from",
    "government", "president", "market", "economy", "policy", "report",
    "officials", "according", "statement", "announced", "election", "inflation",
    "climate", "technology", "investment", "billion", "million", "growth",
    "said", "year", "new", "could", "would", "about", "more", "been", "has"
]

def generate_title():
    """Generate a news-like title."""
    patterns = [
        "{topic}: {action} {subject}",
        "Breaking: {subject} {action} {modifier}",
        "{subject} announces {topic} {modifier}",
        "Report: {topic} {action} amid {subject}",
        "{subject} faces {topic} challenges"
    ]
    pattern = random.choice(patterns)
    return pattern.format(
        topic=random.choice(TOPICS).title(),
        action=random.choice(["rises", "falls", "shifts", "changes", "grows"]),
        subject=random.choice(["market", "government", "officials", "industry", "sector"]),
        modifier=random.choice(["concerns", "uncertainty", "growth", "decline", "pressure"])
    )

def generate_article(word_count: int) -> str:
    """Generate a fake article body."""
    paragraphs = []
    words_remaining = word_count
    
    while words_remaining > 0:
        para_length = min(random.randint(40, 100), words_remaining)
        paragraph = " ".join(random.choices(WORDS, k=para_length))
        # Capitalize first word, add period
        paragraph = paragraph.capitalize() + "."
        paragraphs.append(paragraph)
        words_remaining -= para_length
    
    return "\n\n".join(paragraphs)

def generate_date(start_year: int = 2020, end_year: int = 2024) -> str:
    """Generate a random date string."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date = start + timedelta(days=random_days)
    return date.strftime("%Y-%m-%d")

def estimate_row_bytes(row: dict) -> int:
    """Estimate CSV row size."""
    return sum(len(str(v)) for v in row.values()) + len(row)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if OUTPUT_FILE.exists():
        print(f"File exists: {OUTPUT_FILE}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted.")
            return
    
    target_bytes = TARGET_SIZE_GB * (1024**3)
    bytes_written = 0
    rows_written = 0
    
    print(f"Generating {TARGET_SIZE_GB}GB of synthetic news data...")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "text", "url", "domain"])
        writer.writeheader()
        
        pbar = tqdm(total=TARGET_SIZE_GB, unit='GB', desc="Generating")
        last_gb = 0
        
        while bytes_written < target_bytes:
            domain = random.choice(DOMAINS)
            date = generate_date()
            title = generate_title()
            word_count = random.randint(200, 1500)
            text = generate_article(word_count)
            
            row = {
                "date": date,
                "title": title,
                "text": text,
                "url": f"https://{domain}/article/{random.randint(100000, 999999)}",
                "domain": domain
            }
            
            writer.writerow(row)
            
            row_bytes = estimate_row_bytes(row)
            bytes_written += row_bytes
            rows_written += 1
            
            current_gb = bytes_written / (1024**3)
            if current_gb - last_gb >= 0.1:
                pbar.update(current_gb - last_gb)
                last_gb = current_gb
        
        pbar.close()
    
    actual_size_gb = OUTPUT_FILE.stat().st_size / (1024**3)
    print()
    print("=" * 50)
    print(f"Generation complete!")
    print(f"  Rows: {rows_written:,}")
    print(f"  Size: {actual_size_gb:.2f} GB")
    print(f"  Location: {OUTPUT_FILE}")
    print("=" * 50)
    print()
    print("NOTE: This is SYNTHETIC data. For real data, use download_data.py")

if __name__ == "__main__":
    main()
