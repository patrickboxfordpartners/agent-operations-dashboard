"""Cost tracking and monitoring"""
import logging
from datetime import datetime, date
from typing import Optional
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('second-brain.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('second-brain')

class CostTracker:
    """Track AI API costs"""

    def __init__(self, daily_limit: float = 100.0):
        self.daily_limit = daily_limit
        self.current_spend = 0.0
        self.reset_date = date.today()
        self.log_path = Path("storage/cost_log.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record_spend(self, cost: float, model: str):
        """Record spend and check budget"""

        # Reset if new day
        if date.today() > self.reset_date:
            logger.info(f"Daily spend reset: ${self.current_spend:.2f} spent on {self.reset_date}")
            self.current_spend = 0.0
            self.reset_date = date.today()

        self.current_spend += cost

        # Log to file
        with open(self.log_path, 'a') as f:
            f.write(f'{{"timestamp": "{datetime.now().isoformat()}", "model": "{model}", "cost": {cost:.6f}, "daily_total": {self.current_spend:.2f}}}\n')

        # Alert at threshold
        if self.current_spend > self.daily_limit * 0.8 and self.current_spend - cost <= self.daily_limit * 0.8:
            logger.warning(f"⚠️  Approaching daily limit: ${self.current_spend:.2f} / ${self.daily_limit:.2f}")

        # Hard stop at limit
        if self.current_spend > self.daily_limit:
            logger.error(f"🚨 Daily limit exceeded: ${self.current_spend:.2f} / ${self.daily_limit:.2f}")
            raise RuntimeError("Daily AI spend limit exceeded. Requests will be queued.")

    def get_remaining_budget(self) -> float:
        """Get remaining budget for today"""
        if date.today() > self.reset_date:
            return self.daily_limit
        return max(0, self.daily_limit - self.current_spend)

    def get_spend_summary(self) -> dict:
        """Get spending summary"""
        return {
            "date": self.reset_date.isoformat(),
            "spent": self.current_spend,
            "limit": self.daily_limit,
            "remaining": self.get_remaining_budget(),
            "utilization": self.current_spend / self.daily_limit if self.daily_limit > 0 else 0
        }

# Singleton instance
from .config import config
cost_tracker = CostTracker(daily_limit=config.DAILY_SPEND_LIMIT)
