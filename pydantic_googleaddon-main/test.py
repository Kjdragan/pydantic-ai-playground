import asyncio
from web_tool import WebTool

async def main():
    # Initialize the web tool with debug mode
    web_tool = WebTool(num_results=3)
    WebTool.DEBUG = True  # Enable debug logging
    
    # Example search
    query = "J. Gravelle computer programmer"
    print(f"\nSearching for: {query}")
    print("=" * 50)
    
    try:
        # Perform the search
        results = web_tool.search(query)
        
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Description: {result['description']}")
        
        # Get content from first result
        if results:
            first_url = results[0]['url']
            print(f"\nFetching content from first result: {first_url}")
            print("=" * 50)
            
            content = web_tool.get_web_content(first_url)
            print("\nContent Preview:")
            print(content[:500] + "...")
            
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
