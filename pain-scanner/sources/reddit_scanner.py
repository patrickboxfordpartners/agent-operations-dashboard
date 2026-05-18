"""Reddit pain point scanner"""
import praw
from typing import Optional

class RedditScanner:
    """Scans Reddit for pain points in specific subreddits"""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Reddit scanner

        Note: Reddit API requires registration at https://www.reddit.com/prefs/apps
        For now, we'll use public scraping (no auth needed for read-only)
        """
        if client_id and client_secret:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="pain-scanner/0.1"
            )
        else:
            # Read-only mode
            self.reddit = praw.Reddit(
                client_id="dummy",
                client_secret="dummy",
                user_agent="pain-scanner/0.1"
            )

    def scan_subreddit(self, subreddit_name: str, limit: int = 50) -> list[dict]:
        """
        Scan a subreddit for pain-related posts

        Args:
            subreddit_name: Subreddit to scan (without r/)
            limit: Number of recent posts to check

        Returns:
            List of relevant posts with title, body, url
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            posts = []
            for submission in subreddit.hot(limit=limit):
                # Look for pain indicators in title/body
                pain_keywords = [
                    "problem", "issue", "frustrated", "struggling", "pain",
                    "manual", "tedious", "time consuming", "inefficient",
                    "help", "advice", "solution", "better way"
                ]

                text = (submission.title + " " + submission.selftext).lower()

                if any(keyword in text for keyword in pain_keywords):
                    posts.append({
                        "title": submission.title,
                        "body": submission.selftext,
                        "url": f"https://reddit.com{submission.permalink}",
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "created": submission.created_utc
                    })

            return posts

        except Exception as e:
            print(f"Error scanning r/{subreddit_name}: {e}")
            return []

# For testing without Reddit API
MOCK_REDDIT_DATA = {
    "smallbusiness": [
        {
            "title": "Spending 10+ hours/week on invoicing - is there a better way?",
            "body": "I run a small consulting business (just me + 2 contractors). Every week I spend at least 10 hours creating invoices, tracking time, following up on payments. Using QuickBooks but still so manual. Is there an AI tool that can automate this?",
            "url": "https://reddit.com/r/smallbusiness/example1",
            "score": 45,
            "num_comments": 23
        },
        {
            "title": "Client onboarding is killing me",
            "body": "Small law firm here. New client onboarding takes 2-3 hours per client. Forms, contracts, intake calls, setting up files. We're at capacity and can't take more clients because onboarding is so time consuming. Help!",
            "url": "https://reddit.com/r/smallbusiness/example2",
            "score": 67,
            "num_comments": 31
        }
    ],
    "dentistry": [
        {
            "title": "Appointment no-shows are costing us thousands",
            "body": "We send reminder emails and texts but still getting 15-20% no-show rate. Each no-show costs us $200-300 in lost revenue. Manual follow-up isn't working. What are other practices doing?",
            "url": "https://reddit.com/r/dentistry/example3",
            "score": 89,
            "num_comments": 42
        }
    ]
}

def get_mock_data(subreddit: str) -> list[dict]:
    """Get mock data for testing without Reddit API"""
    return MOCK_REDDIT_DATA.get(subreddit, [])
