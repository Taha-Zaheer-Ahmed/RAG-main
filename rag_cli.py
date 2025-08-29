#!/usr/bin/env python3
"""
Robust RAG CLI System
Query your indexed documents using natural language
"""

import argparse
import sys
from rag_retriever import rag_retriever

def display_results(results, query, show_scores=True, max_results=None):
    """Display search results in a formatted way"""
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Found {len(results)} results")
    print("=" * 80)
    
    if max_results:
        results = results[:max_results]
    
    for i, result in enumerate(results, 1):
        print(f"\n📄 Result {i}:")
        print(f"   Section ID: {result['id']}")
        if show_scores:
            print(f"   Relevance Score: {result['score']:.3f}")
        print(f"   File: {result.get('file', 'Unknown')}")
        print(f"   Content:\n{result['text']}")
        print("-" * 80)

def interactive_mode():
    """Interactive mode for continuous querying"""
    print("🚀 RAG Interactive Mode")
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for commands")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n❓ Enter your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif query.lower() in ['help', 'h']:
                print_help()
                continue
            elif not query:
                continue
            
            # Get number of results
            try:
                k = int(input("📊 How many results? (default: 3): ") or "3")
            except ValueError:
                k = 3
            
            # Search and display
            results = rag_retriever.search(query, k=k)
            display_results(results, query, show_scores=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def print_help():
    """Print help information"""
    help_text = """
📚 RAG CLI Help

Commands:
  help, h     - Show this help
  quit, q     - Exit the program
  exit        - Exit the program

Query Examples:
  - "What are the renewable energy rates for 2025?"
  - "What challenges does Solaria face?"
  - "Tell me about wind energy adoption"
  - "What are the benefits of renewable energy?"

Features:
  - Natural language queries
  - Relevance scoring
  - Configurable result count
  - Interactive mode
  - Batch mode
"""
    print(help_text)

def main():
    parser = argparse.ArgumentParser(
        description="RAG CLI - Query your indexed documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rag_cli.py "renewable energy 2025"
  python rag_cli.py "Solaria challenges" --count 5
  python rag_cli.py --interactive
        """
    )
    
    parser.add_argument(
        "query", 
        nargs="?", 
        help="Query to search for"
    )
    
    parser.add_argument(
        "-c", "--count", 
        type=int, 
        default=3,
        help="Number of results to return (default: 3)"
    )
    
    parser.add_argument(
        "-i", "--interactive", 
        action="store_true",
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "--no-scores", 
        action="store_true",
        help="Hide relevance scores"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or not args.query:
        interactive_mode()
        return
    
    # Single query mode
    try:
        if args.verbose:
            print(f"🔍 Searching for: '{args.query}'")
            print(f"📊 Requesting {args.count} results")
        
        results = rag_retriever.search(args.query, k=args.count)
        
        if not results:
            print(f"❌ No results found for: '{args.query}'")
            return
        
        display_results(
            results, 
            args.query, 
            show_scores=not args.no_scores,
            max_results=args.count
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
