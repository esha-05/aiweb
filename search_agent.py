import os
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError
from tavily import TavilyClient

load_dotenv()

client = Groq()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

def search_and_answer(query: str) -> dict:

    # Step 1: Web search via Tavily
    print(f"🔍 Searching for: {query}")
    try:
        search_results = tavily.search(
            query=query,
            max_results=5,
            include_raw_content=True,
            search_depth="advanced"
        )
    except Exception as e:
        print(f"❌ Tavily search failed: {e}")
        return {
            "answer": "Search service is currently unavailable. Please try again later.",
            "sources": [],
            "error": "search_failed"
        }

    # Step 2: Extract content from results
    sources = []
    context_blocks = []

    for result in search_results.get("results", []):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("raw_content") or result.get("content", "")
        content = content[:3000] if content else ""

        sources.append({"title": title, "url": url})
        context_blocks.append(f"Source: {title}\nURL: {url}\nContent:\n{content}")

    combined_context = "\n\n---\n\n".join(context_blocks)

    # Step 3: Call Groq LLM with model fallback
    print("🤖 Generating answer with Groq...")
    last_error = None

    for model in FALLBACK_MODELS:
        try:
            print(f"   Trying model: {model}")
            response = client.chat.completions.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant that answers questions
using real-time web search results.

Rules:
- Answer clearly and concisely based ONLY on the provided search results
- If the search results don't contain the answer, say so
- Always be factual
- Format your answer in plain text, no markdown"""
                    },
                    {
                        "role": "user",
                        "content": f"""User Question: {query}

Here are the top web search results:

{combined_context}

Please answer the user's question based on these search results."""
                    }
                ]
            )
            answer = response.choices[0].message.content
            print(f"✅ Success with model: {model}")
            return {
                "answer": answer,
                "sources": sources,
                "model_used": model
            }

        except RateLimitError as e:
            print(f"⚠️ Rate limit hit for {model}: {e}")
            last_error = "rate_limit"
            continue  # try next model

        except APIError as e:
            print(f"❌ API error for {model}: {e}")
            last_error = "api_error"
            continue

        except Exception as e:
            print(f"❌ Unexpected error for {model}: {e}")
            last_error = str(e)
            continue

    # All models exhausted
    return {
        "answer": "⚠️ All AI models are currently rate-limited or unavailable. Please try again in 30 minutes.",
        "sources": sources,
        "error": last_error
    }


# Main Function
if __name__ == "__main__":
    print("🔍 AI Web Search Agent")
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    exit_phrases = ["exit", "quit", "bye", "goodbye", "thanks", "thank you",
                    "thankyou", "thanls", "thx", "ok bye", "see ya"]

    while True:
        query = input("You: ").strip()

        if any(phrase in query.lower() for phrase in exit_phrases):
            print("Glad I could help! Thankyou!")
            break

        if not query:
            print("Please enter a question.\n")
            continue

        print("\nSearching...\n")
        result = search_and_answer(query)

        print("✅ ANSWER:")
        print(result["answer"])
        print("\n🔗 SOURCES:")
        for s in result["sources"]:
            print(f"  - {s['title']}: {s['url']}")
        print("\n" + "─"*50 + "\n")