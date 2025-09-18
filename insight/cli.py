import argparse
import json
import sys
from typing import List, Dict, Any, Optional

from .engine import rank, score_candidate
from .metrics import distinct_n, repeat_penalty, brevity_prior, bleu_like, composite, evaluate_text, evaluate_candidates

def main():
    parser = argparse.ArgumentParser(description="Insight Engine CLI for prompt evaluation and ranking.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Rank command
    rank_parser = subparsers.add_parser("rank", help="Rank candidate prompts based on novelty, coherence, and brevity.")
    rank_parser.add_argument("--prompt", type=str, required=True, help="The original prompt text.")
    rank_parser.add_argument("--candidates", type=str, nargs="+", required=True, help="List of candidate prompts to rank.")
    rank_parser.add_argument("--k", type=int, default=1, help="Number of top candidates to return.")
    rank_parser.add_argument("--weights", type=json.loads, default=None, help="JSON string for custom weights (e.g., '{\"novelty\":0.5, \"coherence\":0.3, \"brevity\":0.2}')")

    # Score command
    score_parser = subparsers.add_parser("score", help="Score a single candidate prompt.")
    score_parser.add_argument("--prompt", type=str, required=True, help="The original prompt text.")
    score_parser.add_argument("--candidate", type=str, required=True, help="The candidate prompt to score.")

    # Evaluate command (for new metrics)
    eval_parser = subparsers.add_parser("eval", help="Evaluate text or candidates using quantitative metrics.")
    eval_parser.add_argument("--text", type=str, help="Single text to evaluate.")
    eval_parser.add_argument("--references", type=str, nargs="*", default=[], help="Reference texts for BLEU-like score.")
    eval_parser.add_argument("--eval-file", type=str, help="Path to a file containing candidate texts (one per line).")
    eval_parser.add_argument("--eval-json", type=str, help="Path to a JSON file with a list of candidates.")
    eval_parser.add_argument("--weights", type=json.loads, default=None, help="JSON string for custom weights for composite score.")
    eval_parser.add_argument("--detailed", action="store_true", help="Output detailed scores for each metric.")
    eval_parser.add_argument("--output", type=str, help="Output file path for results (JSON).")

    args = parser.parse_args()

    if args.command == "rank":
        results = rank(args.prompt, args.candidates, args.weights, args.k)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.command == "score":
        results = score_candidate(args.prompt, args.candidate)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.command == "eval":
        candidates_to_eval: List[str] = []
        if args.text:
            candidates_to_eval.append(args.text)
        if args.eval_file:
            with open(args.eval_file, 'r', encoding='utf-8') as f:
                candidates_to_eval.extend([line.strip() for line in f if line.strip()])
        if args.eval_json:
            with open(args.eval_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    candidates_to_eval.extend([str(item) for item in data])
                else:
                    print("Error: JSON file must contain a list of candidates.", file=sys.stderr)
                    sys.exit(1)
        
        if not candidates_to_eval:
            print("Error: No text or candidates provided for evaluation.", file=sys.stderr)
            sys.exit(1)

        if len(candidates_to_eval) == 1 and not args.eval_file and not args.eval_json:
            # Single text evaluation
            result = evaluate_text(candidates_to_eval[0], args.references, args.weights, args.detailed)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Multiple candidates evaluation (ranking)
            results = evaluate_candidates(candidates_to_eval, args.references, args.weights, args.detailed)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"Evaluation results saved to {args.output}")
            else:
                print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()