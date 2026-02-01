import time
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class BenchmarkResult:
    model: str
    prompt: str
    response: str
    ttft: float  # Time to first token
    total_latency: float
    output_tokens: int
    input_tokens: int
    tps: float  # Tokens per second
    cost: float
    success: bool
    quality_score: float = 0.0 # New field for Efficiency Frontier
    error: Optional[str] = None

class MetricsCalculator:
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        # Simplified pricing model (approximate per 1K tokens)
        # In a real app, this would use a more robust pricing dictionary/API
        prices = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "claude-3-5-sonnet-20240620": {"input": 0.003, "output": 0.015},
            "gemini/gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
        }
        
        # Default to a generic price if not found
        price = prices.get(model, {"input": 0.001, "output": 0.002})
        
        total_cost = (input_tokens / 1000) * price["input"] + (output_tokens / 1000) * price["output"]
        return total_cost

    @staticmethod
    def calculate_tps(output_tokens: int, total_latency: float) -> float:
        if total_latency == 0:
            return 0.0
        return output_tokens / total_latency
