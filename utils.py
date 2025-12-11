"""
Utility functions for the 20Q game.
Handles OpenAI API interactions and game logic.
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client lazily
_client = None

def get_client():
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it in Streamlit Cloud secrets or your .env file."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def initialize_game() -> List[Dict[str, str]]:
    """
    Initialize the game with a system prompt.
    Returns the initial conversation history.
    """
    system_prompt = """You are playing a game of 20 Questions. The player is thinking of an English word, and you need to guess it by asking yes/no questions.

Rules:
- Ask one question at a time
- Questions should be yes/no questions
- The player can answer: "Yes", "No", "Sometimes", or "Unknown"
- Try to guess the word within 20 questions (you can use up to 25 if needed)
- When you are confident you know the word, make a guess using the format: "GUESS: [word]" (e.g., "GUESS: elephant")
- If you're not sure but want to test a hypothesis, you can ask "Is it [word]?" as a question
- Be strategic with your questions to narrow down possibilities
- Start with broad questions and get more specific as you learn more
- Use the conversation history to build context and make smarter guesses

Begin by asking your first question."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "I'm ready to play 20 Questions! Think of an English word, and I'll try to guess it. Let me start with my first question:"}
    ]


def get_ai_question(conversation_history: List[Dict[str, str]]) -> str:
    """
    Get the next question or guess from the AI.
    
    Args:
        conversation_history: List of message dictionaries with role and content
        
    Returns:
        The AI's question or guess as a string
    """
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=conversation_history,
            temperature=0.7,
            max_tokens=150
        )
        
        ai_message = response.choices[0].message.content.strip()
        return ai_message
    except ValueError as e:
        return f"Configuration Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}. Please check your API key and try again."


def add_player_answer(conversation_history: List[Dict[str, str]], answer: str) -> None:
    """
    Add the player's answer to the conversation history.
    
    Args:
        conversation_history: List of message dictionaries
        answer: Player's answer ("Yes", "No", "Sometimes", or "Unknown")
    """
    conversation_history.append({"role": "user", "content": answer})


def check_for_guess(message: str) -> Optional[str]:
    """
    Check if the AI message contains a guess.
    Guesses are in the format "GUESS: [word]" or similar patterns.
    
    Args:
        message: The AI's message
        
    Returns:
        The guessed word if found, None otherwise
    """
    import re
    
    message_lower = message.lower()
    
    # Check for explicit "GUESS:" format (case insensitive)
    guess_match = re.search(r'guess\s*:\s*([^\s\.\?!]+)', message_lower)
    if guess_match:
        guess = guess_match.group(1).strip()
        guess = guess.replace('"', '').replace("'", "").strip()
        if guess and len(guess) > 1:
            return guess
    
    # Check for "Is it [word]?" pattern (common guess format)
    # Handle both "Is it word?" and "Is it a/an/the word?" patterns
    is_it_match = re.search(r'is\s+it\s+(?:a|an|the\s+)?([^\s\.\?!]+)', message_lower)
    if is_it_match:
        guess = is_it_match.group(1).strip()
        guess = guess.replace('"', '').replace("'", "").strip()
        # Filter out common question words and articles
        if guess and len(guess) > 1 and guess not in ['a', 'an', 'the']:
            return guess
    
    # Check for other common guess patterns
    guess_patterns = [
        (r"i\s+think\s+it'?s\s+([^\s\.\?!]+)", 1),
        (r"i\s+believe\s+it'?s\s+([^\s\.\?!]+)", 1),
        (r"it\s+must\s+be\s+([^\s\.\?!]+)", 1),
        (r"the\s+word\s+is\s+([^\s\.\?!]+)", 1),
        (r"my\s+guess\s+is\s+([^\s\.\?!]+)", 1),
    ]
    
    for pattern, group_num in guess_patterns:
        match = re.search(pattern, message_lower)
        if match:
            guess = match.group(group_num).strip()
            guess = guess.replace('"', '').replace("'", "").strip()
            # Remove common articles and filter short words
            if guess and len(guess) > 1 and guess not in ['a', 'an', 'the']:
                return guess
    
    return None


def format_conversation_history(conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format conversation history for display, excluding system messages.
    
    Args:
        conversation_history: Full conversation history
        
    Returns:
        Formatted history without system messages
    """
    formatted = []
    for msg in conversation_history:
        if msg["role"] != "system":
            formatted.append(msg)
    return formatted

