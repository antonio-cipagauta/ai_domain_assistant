import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_alternative_domains(
    domain: str, excluded_domains: list[str] = None, context: str = None
) -> list[str]:
    """Generates alternative domain names using Gemini, optionally using RAG context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ["Error: GEMINI_API_KEY not found in environment variables."]

    client = genai.Client(api_key=api_key)

    exclusion_clause = ""
    if excluded_domains:
        exclusion_clause = (
            "\nIMPORTANT: DO NOT suggest any of these domains as they are "
            f"already known or taken: {', '.join(excluded_domains)}"
        )

    context_clause = ""
    if context:
        context_clause = (
            f"\nUSE THIS EXPERT KNOWLEDGE TO INFORM YOUR SUGGESTIONS:\n{context}\n"
        )

    import textwrap

    prompt = textwrap.dedent(f"""
        The domain name '{domain}' is currently unavailable.
        
        You are an expert brand naming consultant and SEO specialist.{context_clause}
        
        Please generate a Python list of exactly 10 creative, catchy, and 
        highly similar alternative domain names.{exclusion_clause}
        
        CRITICAL RULES:
        1. The alternatives MUST be extremely similar in meaning, tone, or 
           structure to the original '{domain}'.
        2. Try slight spelling variations, adding short prefix/suffix words 
           (e.g., 'get', 'try', 'app', 'hq'), or using synonyms for the core concept.
        3. Include a mix of standard (.com) and modern TLDs (.co, .io, .ai, .app, .net).
        4. Only return a raw Python list of strings. NO markdown, NO explanations, 
           NO intro text.
        
        Example format: ["similar1.com", "getsimilar.io", "similarapp.co"]
    """).strip()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        # Quick parsing in case the output is wrapped in markdown code blocks
        text = response.text.strip()
        if text.startswith("```python"):
            text = text[9:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        import ast

        suggestions = ast.literal_eval(text.strip())
        if isinstance(suggestions, list):
            return suggestions
        else:
            return ["Error parsing AI response. Please try again."]

    except Exception as e:
        return [f"Error generating suggestions: {str(e)}"]


if __name__ == "__main__":
    print(get_alternative_domains("google.com"))
