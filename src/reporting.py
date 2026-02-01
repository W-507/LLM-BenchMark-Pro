import pandas as pd
from typing import List
from .metrics import BenchmarkResult, asdict

class ReportGenerator:
    @staticmethod
    def generate_dataframe(results: List[BenchmarkResult]) -> pd.DataFrame:
        data = [asdict(r) for r in results]
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def save_report(df: pd.DataFrame, output_path: str = "benchmark_results.csv"):
        df.to_csv(output_path, index=False)
        print(f"Report saved to {output_path}")
