import argparse
import yaml
import os
from dotenv import load_dotenv
from src.benchmark import BenchmarkEngine

# Load environment variables
load_dotenv()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="LLM-BenchMark-Pro CLI")
    parser.add_argument('--config', type=str, default='config/standard_test.yaml', help='Path to configuration file')
    args = parser.parse_args()

    config = load_config(args.config)
    print(f"Starting benchmark: {config['benchmark_name']}")
    print(f"Models to test: {config['models']}")
    
    print(f"Models to test: {config['models']}")
    
    engine = BenchmarkEngine(config)
    # asyncio.run is needed to run async code from sync main
    import asyncio
    import sys
    
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    results = asyncio.run(engine.run_benchmarks())
    
    # Run evaluation
    from src.evaluation import EvaluationEngine
    eval_engine = EvaluationEngine()
    # This now returns a dataframe with quality_score
    df = eval_engine.evaluate_results(results)
    
    if df.empty:
         from src.reporting import ReportGenerator
         df = ReportGenerator.generate_dataframe(results)

    print("\nBenchmark Results:")
    cols_to_show = ['model', 'ttft', 'tps', 'cost', 'success']
    if 'quality_score' in df.columns:
        cols_to_show.append('quality_score')
    print(df[cols_to_show])
    
    from src.reporting import ReportGenerator
    output_file = f"results_{config['benchmark_name'].replace(' ', '_').lower()}.csv"
    ReportGenerator.save_report(df, output_file)

if __name__ == "__main__":
    main()
