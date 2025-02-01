import asyncio
from web_tool import WebTool
from typing import List, Dict, Any
import json

async def search_and_analyze(queries: List[str], results_per_query: int = 5):
    """
    Perform searches for multiple queries and analyze the results.
    
    Args:
        queries: List of search queries
        results_per_query: Number of results to fetch per query
    """
    # Initialize WebTool with custom settings
    web_tool = WebTool(num_results=results_per_query)
    WebTool.DEBUG = True  # Enable debug mode
    
    all_results = {}
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Searching for: {query}")
        print(f"{'='*50}")
        
        try:
            # Perform search
            results = web_tool.search(query)
            all_results[query] = results
            
            # Display results summary
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Description: {result['description'][:200]}...")
            
            # Get detailed content from first result
            if results:
                first_url = results[0]['url']
                print(f"\nExtracting content from top result: {first_url}")
                try:
                    content = web_tool.get_web_content(first_url)
                    print("\nContent Preview (first 300 chars):")
                    print(content[:300] + "...")
                    
                    # Save content to file
                    filename = f"content_{query.replace(' ', '_')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"\nFull content saved to {filename}")
                    
                except Exception as e:
                    print(f"Error extracting content: {str(e)}")
        
        except Exception as e:
            print(f"Error processing query '{query}': {str(e)}")
    
    # Save all results to JSON
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("\nAll search results saved to search_results.json")

async def main():
    # Example queries
    queries = [
        "Python web scraping best practices",
        "Latest AI developments 2024",
        "Climate change solutions"
    ]
    
    await search_and_analyze(queries, results_per_query=3)

if __name__ == "__main__":
    asyncio.run(main())
