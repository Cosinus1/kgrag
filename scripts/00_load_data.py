# scripts/00_load_data.py

from datasets import load_dataset
from pathlib import Path

def main():
    # Configuration
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    num_articles = 1000
    
    print("="*60)
    print("French Wikipedia Data Loader")
    print("="*60)
    print(f"\nLoading dataset (cached after first download)...")
    print("This uses the cached data - no re-download needed!\n")
    
    # Load French Wikipedia - this will use the cache from your previous download
    # The dataset is already downloaded, so this should be fast
    dataset = load_dataset("wikimedia/wikipedia", "20231101.fr", split="train")
    
    print(f"✓ Dataset loaded! Total articles available: {len(dataset):,}")
    print(f"\n📝 Saving {num_articles} articles to {output_dir}/...\n")
    
    # Save sample to your data/raw folder
    sample = dataset.select(range(num_articles))
    
    saved_count = 0
    errors = 0
    
    for i, article in enumerate(sample):
        try:
            # FIX 1: Use UTF-8 encoding explicitly
            # FIX 2: Add error handling for individual articles
            filename = output_dir / f"wiki_{i:04d}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:  # ← UTF-8 encoding added here!
                f.write(f"# {article['title']}\n\n")
                f.write(article["text"])
            
            saved_count += 1
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{num_articles} articles saved...")
                
        except Exception as e:
            errors += 1
            print(f"⚠️  Error saving article {i} ({article.get('title', 'unknown')}): {e}")
            continue
    
    print(f"\n{'='*60}")
    print("COMPLETE!")
    print(f"{'='*60}")
    print(f"✅ Successfully saved: {saved_count} articles")
    if errors > 0:
        print(f"⚠️  Errors: {errors} articles")
    print(f"📁 Location: {output_dir.absolute()}")
    print(f"\nNext step: python scripts/01_prepare_corpus.py")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()