import openai
from .config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_summary(content: str) -> str:
    # Truncate content to avoid exceeding token limits for the API call
    # A common token-to-word ratio is ~4 chars/token, so 3000 tokens is ~12000 chars
    max_chars = 12000
    truncated_content = content[:max_chars]

    prompt = f"""
    Please provide a concise, clear, and easy-to-understand summary of the following text.
    The summary should capture the main points and key takeaways.

    Text to summarize:
    ---
    {truncated_content}
    ---
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # A little creativity, but still factual
            max_tokens=500,
        )
        summary = response.choices[0].message.content
        return summary.strip() if summary else "Could not generate a summary."
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return "Error: Summary generation failed."
