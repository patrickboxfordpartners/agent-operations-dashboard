#!/usr/bin/env python3
"""Test the pain scanner"""
import asyncio
import json
import os
from dotenv import load_dotenv

from sources.reddit_scanner import get_mock_data
from analysis.pain_extractor import PainExtractor

load_dotenv()

# Verticals to monitor
TEST_VERTICALS = [
    {
        "name": "small business",
        "subreddits": ["smallbusiness"],
        "keywords": ["automation", "manual", "time consuming", "inefficient"]
    },
    {
        "name": "healthcare",
        "subreddits": ["dentistry"],
        "keywords": ["scheduling", "patient", "manual", "paperwork"]
    }
]

async def test_pain_scanner():
    """Test pain scanner with mock data"""

    print("\n🔍 Testing Pain Scanner\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    extractor = PainExtractor(api_key)

    all_pain_points = []

    for vertical_config in TEST_VERTICALS:
        print(f"\n📊 Scanning: {vertical_config['name']}")
        print("-" * 70)

        for subreddit in vertical_config['subreddits']:
            print(f"  📡 r/{subreddit}...")

            # Get mock data (in production, use RedditScanner)
            posts = get_mock_data(subreddit)
            print(f"     Found {len(posts)} relevant posts")

            if posts:
                # Extract pain points
                print(f"     🧠 Analyzing with Claude...")
                pain_points = await extractor.extract_from_posts(
                    posts=posts,
                    vertical=vertical_config['name'],
                    source="reddit"
                )

                print(f"     ✅ Extracted {len(pain_points)} pain points")

                for pp in pain_points:
                    print(f"\n     💡 {pp.title}")
                    print(f"        Frequency: {pp.frequency} | Urgency: {pp.urgency}")
                    print(f"        Market: {pp.estimated_market_size} businesses")
                    print(f"        Solution: {pp.proposed_solution[:80]}...")
                    print(f"        ROI: {pp.estimated_roi}")

                all_pain_points.extend(pain_points)

    # Save results
    print("\n" + "=" * 70)
    output_file = "discovered_pain_points.json"
    with open(output_file, 'w') as f:
        json.dump(
            [pp.model_dump() for pp in all_pain_points],
            f,
            indent=2,
            default=str
        )

    print(f"\n✅ Discovered {len(all_pain_points)} pain points")
    print(f"📄 Saved to: {output_file}\n")

    print("💡 Next steps:")
    print("   1. Review discovered pain points")
    print("   2. Turn high-priority pains into Workflow Auditor test cases")
    print("   3. Use for content ideas (Content Engine)")
    print("   4. Set up cron job to run daily")
    print("   5. Add real Reddit API credentials for live scanning\n")

if __name__ == "__main__":
    asyncio.run(test_pain_scanner())
