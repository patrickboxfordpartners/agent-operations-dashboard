#!/usr/bin/env python3
"""Test content engine"""
import asyncio
import os
from dotenv import load_dotenv

from shared.models import ContentRequest
from generation.content_generator import ContentGenerator

load_dotenv()

# Test content requests
TEST_REQUESTS = [
    ContentRequest(
        content_type="linkedin_post",
        topic="How we cut scheduling time by 68% for a dental practice",
        key_points=[
            "Front desk spending 15 hrs/week on scheduling",
            "Built AI assistant with Make + Claude",
            "Reduced to 5 hrs/week (68% savings)",
            "Payback in 3.4 months"
        ],
        tone="professional"
    ),
    ContentRequest(
        content_type="twitter_thread",
        topic="5 signs your business is ready for AI automation",
        key_points=[
            "Repetitive manual tasks taking 10+ hours/week",
            "Team at capacity but can't hire",
            "Errors from manual data entry",
            "Customer experience suffering from delays",
            "Budget exists but unsure where to start"
        ],
        tone="casual"
    ),
    ContentRequest(
        content_type="email_newsletter",
        topic="Quick win: Automate your client intake in 2 weeks",
        key_points=[
            "Most firms waste 5-10 hours/week on intake",
            "AI can handle form validation, scheduling, CRM entry",
            "Typical ROI: 60-70% time savings",
            "Can be built in 2 weeks with no-code tools"
        ],
        tone="friendly"
    )
]

async def test_content_engine():
    """Test content generation"""

    print("\n✍️  Testing Content Engine\n")
    print("=" * 70)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    generator = ContentGenerator(api_key)

    for i, request in enumerate(TEST_REQUESTS, 1):
        print(f"\n{i}. Generating {request.content_type}...")
        print(f"   Topic: {request.topic}")
        print(f"   Tone: {request.tone}")

        content = await generator.generate(request)

        print(f"\n   ✅ Generated ({len(content.body)} chars)")
        print("\n" + "-" * 70)
        if content.title:
            print(f"TITLE: {content.title}")
            print("-" * 70)
        print(content.body)
        print("-" * 70)

        if content.metadata.get('hashtags'):
            print(f"\nHashtags: {' '.join(content.metadata['hashtags'])}")
        if content.metadata.get('cta'):
            print(f"CTA: {content.metadata['cta']}")

        print("\n" + "=" * 70)

        # Save each piece
        filename = f"generated_{request.content_type}_{i}.txt"
        with open(filename, 'w') as f:
            if content.title:
                f.write(f"{content.title}\n\n")
            f.write(content.body)
        print(f"💾 Saved to: {filename}")

    print("\n✅ Content generation complete!\n")
    print("💡 Next steps:")
    print("   1. Review generated content quality")
    print("   2. Adjust tone/format if needed")
    print("   3. Connect to scheduling/posting tools")
    print("   4. Set up content calendar (weekly generation)")
    print("   5. Feed pain points from Pain Scanner\n")

if __name__ == "__main__":
    asyncio.run(test_content_engine())
