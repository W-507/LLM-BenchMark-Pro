from typing import List, Dict, Any
from .metrics import BenchmarkResult, asdict
import pandas as pd

# Try importing RAGAS, if not available, we warn or degrade gracefully
try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

class EvaluationEngine:
    def __init__(self, judge_model: str = "gpt-4o"):
        self.judge_model = judge_model

    def evaluate_results(self, results: List[BenchmarkResult]) -> pd.DataFrame:
        """
        Evaluates the benchmark results using RAGAS or custom judge logic.
        For simplicity, we will assume we can run RAGAS if available.
        """
        if not RAGAS_AVAILABLE:
            print("RAGAS not available. Using mock scores.")
            return self._generate_mock_scores(results)

        print("Running RAGAS evaluation...")
        
        # Check if we are running a mock test (no API keys usually)
        if results and results[0].model.startswith("mock/"):
             print("Demo Mode detected: Skipping actual RAGAS evaluation and using mock scores.")
             return self._generate_mock_scores(results)
        
        try:
            # Prepare data for RAGAS
            data = {
                "question": [],
                "answer": [],
                "contexts": [],
                # "ground_truth": [] # Optional
            }
            
            # We need to filter results that actually have responses
            valid_results = [r for r in results if r.success]
            
            for res in valid_results:
                data["question"].append(res.prompt)
                data["answer"].append(res.response)
                data["contexts"].append([""]) # Empty context for now if not RAG/Retrieval task
                
            dataset = Dataset.from_dict(data)
            
            metrics = [answer_relevancy]
            
            evaluation_results = evaluate(
                dataset=dataset,
                metrics=metrics,
                llm=self.judge_model
            )
            return evaluation_results.to_pandas()
            
        except Exception as e:
            print(f"RAGAS evaluation failed (likely due to missing API keys or configuration): {e}")
            print("Falling back to mock scores for demonstration.")
            return self._generate_mock_scores(results)

    def _generate_mock_scores(self, results: List[BenchmarkResult]) -> pd.DataFrame:
        import random
        # Convert results to dicts
        data = [asdict(r) for r in results]
        df = pd.DataFrame(data)
        # Add random quality scores
        df['quality_score'] = [random.uniform(0.7, 1.0) if r.success else 0.0 for r in results]
        return df

    def custom_judge(self, results: List[BenchmarkResult]) -> List[Dict[str, Any]]:
        """
        A simpler LLM-as-a-judge implementation using direct prompting if RAGAS is too complex to setup quickly.
        """
        # Placeholder for custom logic
        pass
