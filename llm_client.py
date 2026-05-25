"""
DeepSeek API client with timeout handling and user-friendly errors.
"""

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    OpenAI,
    RateLimitError,
)

DEFAULT_TIMEOUT_SECONDS = 60.0
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekAPIError(Exception):
    """Raised when a DeepSeek request fails in a user-visible way."""

    def __init__(self, user_message):
        self.user_message = user_message
        super().__init__(user_message)


def create_deepseek_client(api_key, timeout=DEFAULT_TIMEOUT_SECONDS):
    """Create an OpenAI-compatible DeepSeek client with a request timeout."""
    return OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        timeout=timeout,
    )


def chat_completion(
    api_key,
    messages,
    model=DEFAULT_MODEL,
    temperature=0.3,
    timeout=DEFAULT_TIMEOUT_SECONDS,
):
    """
    Send a chat completion request to DeepSeek.

    Returns the assistant message text, or raises DeepSeekAPIError.
    """
    try:
        client = create_deepseek_client(api_key, timeout=timeout)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except APITimeoutError as exc:
        raise DeepSeekAPIError(
            "The AI request timed out after 60 seconds. Please try again."
        ) from exc
    except APIConnectionError as exc:
        raise DeepSeekAPIError(
            "Could not connect to DeepSeek. Check your internet connection and try again."
        ) from exc
    except RateLimitError as exc:
        raise DeepSeekAPIError(
            "DeepSeek rate limit reached. Please wait a moment and try again."
        ) from exc
    except APIStatusError as exc:
        raise DeepSeekAPIError(
            f"DeepSeek returned an error (HTTP {exc.status_code}). Please try again later."
        ) from exc
    except Exception as exc:
        raise DeepSeekAPIError(
            "Something went wrong while generating the AI response. Please try again."
        ) from exc
