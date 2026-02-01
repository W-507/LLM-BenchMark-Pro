import time
import litellm
from typing import List, Dict, Any
from .metrics import BenchmarkResult, MetricsCalculator
import asyncio

class BenchmarkEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = config.get("models", [])
        self.prompts = config.get("prompts", [])
        self.max_tokens = config.get("max_tokens", 100)
    
    async def run_single_benchmark(self, model: str, prompt: str) -> BenchmarkResult:
        start_time = time.time()
        ttft = 0.0
        first_token_received = False
        
        try:
            # DEMO MODE: Handle mock models to avoid API calls
            if model.startswith("mock/"):
                import random
                import asyncio
                
                # Simulate network latency
                simulated_latency = random.uniform(0.5, 2.0)
                await asyncio.sleep(simulated_latency)
                
                ttft = random.uniform(0.1, 0.5)
                full_response = "This is a simulated response for demo purposes. " * 5
                total_latency = headers = simulated_latency
                input_tokens = len(prompt.split())
                output_tokens = len(full_response.split())
                
                tps = output_tokens / total_latency
                # Simulate cost based on model name
                base_price = 0.01 if "gpt-4" in model else 0.005
                cost = (input_tokens + output_tokens) / 1000 * base_price
                
                return BenchmarkResult(
                    model=model,
                    prompt=prompt,
                    response=full_response,
                    ttft=ttft,
                    total_latency=total_latency,
                    output_tokens=output_tokens,
                    input_tokens=input_tokens,
                    tps=tps,
                    cost=cost,
                    success=True,
                    quality_score=random.uniform(0.7, 0.99)
                )

            # We use streaming to calculate TTFT
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                stream=True
            )
            
            collected_chunks = []
            async for chunk in response:
                if not first_token_received:
                    ttft = time.time() - start_time
                    first_token_received = True
                
                content = chunk.choices[0].delta.content or ""
                collected_chunks.append(content)
                
            full_response = "".join(collected_chunks)
            end_time = time.time()
            total_latency = end_time - start_time
            
            # Simple token estimation (liteLLM provides usage in non-stream, but stream is trickier)
            # For accurate usage in stream, we can use litellm's token_counter or just approximate/count words
            input_tokens = litellm.token_counter(model=model, text=prompt)
            output_tokens = litellm.token_counter(model=model, text=full_response)
            
            tps = MetricsCalculator.calculate_tps(output_tokens, total_latency)
            cost = MetricsCalculator.calculate_cost(model, input_tokens, output_tokens)
            
            return BenchmarkResult(
                model=model,
                prompt=prompt,
                response=full_response,
                ttft=ttft,
                total_latency=total_latency,
                output_tokens=output_tokens,
                input_tokens=input_tokens,
                tps=tps,
                cost=cost,
                success=True,
                quality_score=0.0 # Default, to be updated by EvaluationEngine
            )
            
        except Exception as e:
            return BenchmarkResult(
                model=model,
                prompt=prompt,
                response="",
                ttft=0.0,
                total_latency=0.0,
                output_tokens=0,
                input_tokens=0,
                tps=0.0,
                cost=0.0,
                success=False,
                error=str(e)
            )

    async def run_benchmarks(self) -> List[BenchmarkResult]:
        tasks = []
        print(f"Preparing to benchmark {len(self.models)} models with {len(self.prompts)} prompts...")
        
        for model in self.models:
            for prompt in self.prompts:
                # Create a task for each model-prompt combination
                tasks.append(self.run_single_benchmark(model, prompt))
        
        print(f"Starting parallel execution of {len(tasks)} benchmarks...")
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        print("All benchmarks completed.")
        return results
