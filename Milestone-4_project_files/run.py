"""
Main entry point for running the AI Paper Review System.
Run this script to see available options.
"""

import os
import sys
import argparse

# Add project root to path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Change to project root
os.chdir(ROOT)


def run_check_imports():
    """Check if all dependencies are installed."""
    print("\n" + "="*60)
    print("Checking Dependencies...")
    print("="*60)
    from scripts.check_imports import main
    main()


def run_workflow_test():
    """Run the workflow test to verify all modules work."""
    print("\n" + "="*60)
    print("Running Workflow Test...")
    print("="*60)
    import test_workflow
    test_workflow.main()


def run_full_pipeline(topic, limit, min_year, min_citations):
    """Run the complete paper processing pipeline."""
    print("\n" + "="*60)
    print("Running Full Pipeline...")
    print("="*60)
    from scripts.prepare_dataset import create_dataset, validate_dataset
    
    stats = create_dataset(
        topic=topic,
        limit=limit,
        year_min=min_year,
        min_citations=min_citations,
        download_pdfs=True
    )
    
    validate_dataset()
    return stats


def run_flask_ui():
    """Launch the Flask web UI."""
    print("\n" + "="*60)
    print("Launching Web UI...")
    print("="*60)
    from ui.app_flask import app
    print("\nOpen http://127.0.0.1:5000 in your browser")
    print("Press Ctrl+C to stop\n")
    app.run(host='127.0.0.1', port=5000, debug=False)


def run_gradio_ui():
    """Launch the Gradio web UI (may have issues with Python 3.13)."""
    print("\n" + "="*60)
    print("Launching Gradio UI...")
    print("="*60)
    print("\nNote: Gradio may have compatibility issues with Python 3.13")
    print("If you encounter errors, use the Flask UI instead (--flask)\n")
    from ui.app import demo
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


def main():
    parser = argparse.ArgumentParser(
        description="AI Paper Review System - Main Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --check          # Check dependencies
  python run.py --test           # Run workflow test
  python run.py --ui             # Launch Flask web UI
  python run.py --gradio         # Launch Gradio web UI
  python run.py --run            # Run pipeline with default settings
  python run.py --run --topic "machine learning" --limit 5
        """
    )
    
    parser.add_argument('--check', action='store_true',
                        help='Check if all dependencies are installed')
    parser.add_argument('--test', action='store_true',
                        help='Run workflow test to verify modules')
    parser.add_argument('--ui', '--flask', action='store_true',
                        help='Launch Flask web UI')
    parser.add_argument('--gradio', action='store_true',
                        help='Launch Gradio web UI')
    parser.add_argument('--run', action='store_true',
                        help='Run the full pipeline')
    
    # Pipeline arguments
    parser.add_argument('--topic', type=str, 
                        default='deep learning natural language processing',
                        help='Research topic to search')
    parser.add_argument('--limit', type=int, default=10,
                        help='Maximum number of papers (default: 10)')
    parser.add_argument('--min-year', type=int, default=2020,
                        help='Minimum publication year (default: 2020)')
    parser.add_argument('--min-citations', type=int, default=50,
                        help='Minimum citation count (default: 50)')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        print("\n" + "="*60)
        print("AI Paper Review System")
        print("="*60)
        print("\nAvailable commands:")
        print("  --check     : Check dependencies")
        print("  --test      : Run workflow test")
        print("  --ui        : Launch Flask web UI")
        print("  --gradio    : Launch Gradio web UI")
        print("  --run       : Run full pipeline")
        print("\nFor more options, run: python run.py --help")
        return
    
    # Execute requested action
    if args.check:
        run_check_imports()
    elif args.test:
        run_workflow_test()
    elif args.ui:
        run_flask_ui()
    elif args.gradio:
        run_gradio_ui()
    elif args.run:
        run_full_pipeline(args.topic, args.limit, args.min_year, args.min_citations)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
