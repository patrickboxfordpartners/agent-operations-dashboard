"""AI service clients with error handling and cost tracking"""
import anthropic
import voyageai
import json
import hashlib
from typing import Optional, Literal
from .config import config
from .monitoring import cost_tracker, logger

class AIClient:
    """Unified AI client with cost tracking"""

    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.voyage = voyageai.Client(api_key=config.VOYAGE_API_KEY)

    async def complete(
        self,
        prompt: str,
        model: Literal["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"] = "claude-sonnet-4-6",
        max_tokens: int = 2000,
        system: Optional[str] = None,
        response_format: Literal["text", "json"] = "text"
    ) -> dict:
        """
        Call Claude with cost tracking

        Returns:
            {
                "content": str,
                "usage": {"input_tokens": int, "output_tokens": int},
                "cost": float
            }
        """

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }

            if system:
                kwargs["system"] = system

            response = self.claude.messages.create(**kwargs)

            # Extract content
            if response_format == "json":
                try:
                    text = response.content[0].text

                    # Strip markdown code blocks if present
                    if "```json" in text:
                        # Extract content between ```json and ```
                        start = text.find("```json") + 7
                        end = text.find("```", start)
                        if end != -1:
                            text = text[start:end].strip()
                    elif text.startswith("```"):
                        text = text.replace("```", "").strip()

                    # Try to parse, but use JSONDecoder to stop at first valid object
                    decoder = json.JSONDecoder()
                    content, idx = decoder.raw_decode(text)

                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response: {response.content[0].text[:200]}")
                    content = {"error": "Invalid JSON", "raw": response.content[0].text}
            else:
                content = response.content[0].text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            pricing = config.PRICING[model]
            cost = (input_tokens / 1_000_000 * pricing["input"]) + (output_tokens / 1_000_000 * pricing["output"])

            # Track cost
            cost_tracker.record_spend(cost, model)

            logger.info(f"Claude API call: {model}, {input_tokens}in + {output_tokens}out tokens, ${cost:.4f}")

            return {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                "cost": cost
            }

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def embed(self, texts: list[str], model: str = "voyage-2") -> list[list[float]]:
        """
        Generate embeddings with cost tracking

        Returns:
            List of embedding vectors
        """

        try:
            result = self.voyage.embed(texts, model=model)

            # Estimate tokens (rough: 1 token ~= 4 chars)
            total_chars = sum(len(t) for t in texts)
            estimated_tokens = total_chars // 4

            cost = estimated_tokens / 1_000_000 * config.PRICING[model]
            cost_tracker.record_spend(cost, f"voyage-{model}")

            logger.info(f"Voyage embed: {len(texts)} texts, ~{estimated_tokens} tokens, ${cost:.4f}")

            return result.embeddings

        except Exception as e:
            logger.error(f"Voyage API error: {e}")
            raise

    async def embed_single(self, text: str) -> list[float]:
        """Convenience method for single embedding"""
        embeddings = await self.embed([text])
        return embeddings[0]

# Singleton instance
ai_client = AIClient()
