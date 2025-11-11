import openai
import json
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


def generate_tasks(content: str) -> list:
    """
    Generates a list of tasks (MCQ, open-ended, matching) from the
    given text content.
    """
    # Truncate content to avoid exceeding token limits
    max_chars = 12000
    truncated_content = content[:max_chars]

    system_prompt = """
    You are an expert in education and curriculum design. 
    You will be given a text and your task is to generate a list of 6-7 learning tasks based on it.
    The tasks should be of the following types: 'multiple_choice', 'open_question', or 'matching'.

    You MUST return your answer as a single, valid JSON object in the following format:
    {
      "tasks": [
        {
          "task_type": "multiple_choice",
          "task_data": {
            "question": "What is the main topic?",
            "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
            "correct_answer": "Topic B"
          }
        },
        {
          "task_type": "open_question",
          "task_data": {
            "question": "Explain the concept of X in your own words."
          }
        },
        {
          "task_type": "matching",
          "task_data": {
            "pairs": [
              {"key": "Term 1", "value": "Definition 1"},
              {"key": "Term 2", "value": "Definition 2"}
            ]
          }
        }
      ]
    }
    """

    user_prompt = f"""
    Here is the text to analyze. Generate the tasks based on this content.

    Text:
    ---
    {truncated_content}
    ---
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=2000,
        )

        response_data = json.loads(response.choices[0].message.content)
        return response_data.get("tasks", [])

    except Exception as e:
        print(f"An error occurred with the OpenAI API (Task Generation): {e}")
        return []
