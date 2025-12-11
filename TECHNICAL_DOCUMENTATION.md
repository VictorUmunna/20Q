# Technical Documentation: 20Q Game

This document provides a comprehensive, line-by-line explanation of the entire codebase. It explains the reasoning behind every decision, how components interact, and answers potential questions about the implementation.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Decisions](#architecture--design-decisions)
3. [File Structure](#file-structure)
4. [Dependencies (requirements.txt)](#dependencies-requirementstxt)
5. [Utils Module (utils.py) - Complete Breakdown](#utils-module-utilspy---complete-breakdown)
6. [Main Application (app.py) - Complete Breakdown](#main-application-apppy---complete-breakdown)
7. [Data Flow & State Management](#data-flow--state-management)
8. [Common Questions & Answers](#common-questions--answers)

---

## Project Overview

The 20Q Game is a conversational AI application where an AI tries to guess a word the player is thinking of by asking yes/no questions. The application uses:

- **Streamlit**: For the web interface and UI components
- **OpenAI GPT-4o-mini**: For generating questions and making guesses
- **Python**: As the core programming language

The game maintains conversation history in memory (no database) and passes the full context to the AI model on each turn, allowing it to build understanding progressively.

---

## Architecture & Design Decisions

### Why No Database?

The application doesn't use a database because:
1. **Stateless API calls**: Each OpenAI API call is independent and includes full context
2. **Session-based**: Game state lives only during a user's session
3. **Simplicity**: No need for persistence - games are meant to be played and restarted
4. **Cost efficiency**: Avoiding database operations reduces complexity and costs

### Why Streamlit?

- **Rapid prototyping**: Fast to build interactive UIs
- **Python-native**: Works seamlessly with OpenAI's Python SDK
- **Built-in state management**: `st.session_state` handles user sessions automatically
- **Deployment simplicity**: Streamlit Cloud makes deployment straightforward

### Why GPT-4o-mini?

- **Cost-effective**: Much cheaper than GPT-4 while maintaining good quality
- **Sufficient capability**: Handles the reasoning required for 20 Questions well
- **Fast responses**: Lower latency than larger models
- **Token efficiency**: Smaller context window is fine for 20-question games

---

## File Structure

```
20Q/
├── app.py              # Main Streamlit application (UI and game flow)
├── utils.py            # Business logic and OpenAI API interactions
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in git)
└── README.md           # User-facing documentation
```

**Separation of concerns**: `app.py` handles UI and user interactions, while `utils.py` contains all the game logic and API calls. This makes the code more maintainable and testable.

---

## Dependencies (requirements.txt)

```txt
streamlit>=1.28.0
openai>=1.3.0
python-dotenv>=1.0.0
```

### Line-by-Line Explanation:

**`streamlit>=1.28.0`**
- **What**: Web framework for building the UI
- **Why >=1.28.0**: Ensures we have access to recent features and bug fixes
- **Used for**: Creating buttons, displaying text, managing session state, handling user interactions

**`openai>=1.3.0`**
- **What**: Official OpenAI Python SDK
- **Why >=1.3.0**: Ensures compatibility with the chat completions API
- **Used for**: Making API calls to GPT-4o-mini, sending conversation history, receiving AI responses

**`python-dotenv>=1.0.0`**
- **What**: Library for loading environment variables from `.env` files
- **Why**: Keeps API keys out of code (security best practice)
- **Used for**: Loading `OPENAI_API_KEY` from `.env` file during local development

---

## Utils Module (utils.py) - Complete Breakdown

This module contains all the business logic and OpenAI API interactions. It's separated from the UI code for better organization and testability.

### Imports Section (Lines 1-9)

```python
"""
Utility functions for the 20Q game.
Handles OpenAI API interactions and game logic.
"""
```

**Lines 1-4**: Module docstring explaining the purpose of this file. This helps other developers (and future you) understand what this module does.

```python
import os
```

**Line 6**: Imports Python's built-in `os` module.
- **Why**: Needed to access environment variables via `os.getenv()`
- **Used for**: Reading the `OPENAI_API_KEY` from environment variables

```python
from typing import List, Dict, Optional
```

**Line 7**: Imports type hints from the `typing` module.
- **Why**: Type hints improve code readability and help catch errors early
- **What each does**:
  - `List`: For lists like `List[Dict[str, str]]` (list of dictionaries)
  - `Dict`: For dictionaries like `Dict[str, str]` (string keys, string values)
  - `Optional`: For values that can be `None` or a specific type

```python
from dotenv import load_dotenv
```

**Line 8**: Imports the `load_dotenv` function.
- **Why**: Loads environment variables from a `.env` file
- **How it works**: Reads `.env` file and sets those variables in `os.environ`
- **Security**: Keeps sensitive keys out of source code

```python
from openai import OpenAI
```

**Line 9**: Imports the OpenAI client class.
- **Why**: This is the main class for making API calls to OpenAI
- **Usage**: We'll create an instance of this to interact with GPT models

### Environment Setup (Lines 11-12)

```python
# Load environment variables
load_dotenv()
```

**Line 12**: Calls `load_dotenv()` to load variables from `.env` file.
- **When it runs**: Immediately when the module is imported
- **What it does**: Reads `.env` file (if it exists) and loads variables into `os.environ`
- **Why here**: We need the API key loaded before we try to use it
- **Note**: In production (Streamlit Cloud), this still runs but the `.env` file doesn't exist - variables come from Streamlit secrets instead

### Lazy Client Initialization (Lines 14-28)

```python
# Initialize OpenAI client lazily
_client = None
```

**Line 15**: Creates a module-level variable `_client` initialized to `None`.
- **Why `_client` with underscore**: The underscore prefix indicates it's a private variable (convention, not enforced)
- **Why `None` initially**: We'll create the client only when needed (lazy initialization)
- **Why lazy initialization**: 
  1. **Deployment compatibility**: On Streamlit Cloud, if the API key isn't set, we want to fail gracefully when the function is called, not when the module is imported
  2. **Error handling**: We can provide better error messages when the key is missing
  3. **Performance**: No need to create the client if it's never used

```python
def get_client():
    """Get or create the OpenAI client."""
    global _client
```

**Line 17-19**: Defines a function to get the OpenAI client.
- **Why a function**: Encapsulates the creation logic and allows lazy initialization
- **`global _client`**: Allows us to modify the module-level `_client` variable
- **Why global**: We want to reuse the same client instance across multiple calls (singleton pattern)

```python
    if _client is None:
```

**Line 20**: Checks if the client hasn't been created yet.
- **Why this check**: Ensures we only create the client once (singleton pattern)
- **Performance**: Creating the client is cheap, but reusing it is better practice
- **Thread safety**: In Streamlit's single-threaded execution model, this is safe

```python
        api_key = os.getenv("OPENAI_API_KEY")
```

**Line 21**: Retrieves the API key from environment variables.
- **`os.getenv()`**: Gets the value of the environment variable, returns `None` if not found
- **Why not hardcode**: Security - API keys should never be in source code
- **Where it comes from**: 
  - Local: `.env` file (loaded by `load_dotenv()`)
  - Production: Streamlit Cloud secrets (set in dashboard)

```python
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it in Streamlit Cloud secrets or your .env file."
            )
```

**Lines 22-26**: Validates that the API key exists.
- **Why check here**: Better to fail early with a clear error message
- **`ValueError`**: Appropriate exception type for missing configuration
- **Error message**: Tells the user exactly what's wrong and how to fix it
- **Why not in module-level code**: If we checked at import time, the app would crash immediately. By checking here, we can show a user-friendly error in the UI

```python
        _client = OpenAI(api_key=api_key)
```

**Line 27**: Creates the OpenAI client instance.
- **`OpenAI(api_key=api_key)`**: Initializes the client with the API key
- **What this does**: Sets up the client to make authenticated requests to OpenAI's API
- **Why store in `_client`**: So we can reuse it in future calls (avoids recreating it)

```python
    return _client
```

**Line 28**: Returns the client instance.
- **First call**: Creates and returns a new client
- **Subsequent calls**: Returns the same client instance (singleton)

### Game Initialization (Lines 31-54)

```python
def initialize_game() -> List[Dict[str, str]]:
```

**Line 31**: Defines a function that returns a conversation history list.
- **Return type**: `List[Dict[str, str]]` - a list of dictionaries, each with string keys and string values
- **What it returns**: The initial conversation history with system prompt
- **Why a function**: Allows us to reset the game by calling this again

```python
    """
    Initialize the game with a system prompt.
    Returns the initial conversation history.
    """
```

**Lines 32-35**: Docstring explaining what the function does.

```python
    system_prompt = """You are playing a game of 20 Questions. The player is thinking of an English word, and you need to guess it by asking yes/no questions.
```

**Line 36**: Starts the system prompt string.
- **What is a system prompt**: Instructions that define the AI's role and behavior
- **Why multi-line string**: The prompt is long and needs to be readable
- **First sentence**: Establishes the AI's role and the game context
- **Why explicit**: The model needs clear instructions to behave correctly

```python
Rules:
- Ask one question at a time
```

**Line 38-39**: Rule about question frequency.
- **Why this rule**: Prevents the AI from asking multiple questions at once, which would break the game flow
- **Enforcement**: The model generally follows this, but we could add validation if needed

```python
- Questions should be yes/no questions
```

**Line 40**: Constraint on question type.
- **Why**: The game mechanics require yes/no answers
- **What happens if violated**: The player might not be able to answer properly

```python
- The player can answer: "Yes", "No", "Sometimes", or "Unknown"
```

**Line 41**: Defines valid answer options.
- **Why list these**: So the AI knows what responses to expect
- **"Sometimes"**: Handles ambiguous cases (e.g., "Is it alive?" for "virus")
- **"Unknown"**: Allows players to skip questions they can't answer

```python
- Try to guess the word within 20 questions (you can use up to 25 if needed)
```

**Line 42**: Sets question limit.
- **20 questions**: Standard game rule
- **25 if needed**: Allows flexibility for edge cases
- **Why mention both**: The AI should try to be efficient but has a safety margin

```python
- When you are confident you know the word, make a guess using the format: "GUESS: [word]" (e.g., "GUESS: elephant")
```

**Line 43**: Defines the structured guess format.
- **Why structured format**: Makes it easier to parse guesses programmatically
- **"GUESS:" prefix**: Clear marker that this is a guess, not a question
- **Example**: Helps the model understand the expected format
- **Reality**: Models don't always follow this exactly, which is why we have regex fallbacks

```python
- If you're not sure but want to test a hypothesis, you can ask "Is it [word]?" as a question
```

**Line 44**: Allows the AI to ask questions that are also guesses.
- **Why this flexibility**: Sometimes asking "Is it X?" is more natural than the structured format
- **Distinction**: This is a question (player answers), not a final guess (game ends)

```python
- Be strategic with your questions to narrow down possibilities
```

**Line 45**: Encourages efficient questioning.
- **Why**: Better questions lead to faster guesses
- **Strategy**: Start broad, get specific (e.g., "Is it alive?" → "Is it an animal?" → "Is it a mammal?")

```python
- Start with broad questions and get more specific as you learn more
```

**Line 46**: Provides questioning strategy.
- **Why this strategy**: Maximizes information gain per question
- **Example**: "Is it a living thing?" eliminates half the possibilities

```python
- Use the conversation history to build context and make smarter guesses
```

**Line 47**: Reminds the model to use previous answers.
- **Why needed**: The model receives full history, but explicit reminder helps
- **How it works**: Each API call includes all previous Q&A pairs

```python
Begin by asking your first question."""
```

**Line 49**: Instruction to start the game.
- **Why**: Without this, the model might wait for more instructions
- **Action trigger**: Tells the model to generate the first question immediately

```python
    return [
        {"role": "system", "content": system_prompt},
```

**Line 51-52**: Creates the initial conversation history.
- **Why a list**: OpenAI API expects a list of message objects
- **`{"role": "system", ...}`**: System message sets the AI's behavior
- **Why system role**: Separate from user/assistant messages, defines the AI's persona

```python
        {"role": "assistant", "content": "I'm ready to play 20 Questions! Think of an English word, and I'll try to guess it. Let me start with my first question:"}
    ]
```

**Line 53**: Adds an initial assistant message.
- **Why include this**: Provides context that the game is starting
- **"Let me start with my first question:"**: Prompts the model to generate a question
- **Why not just system prompt**: The model needs an assistant message to continue from

### Getting AI Questions (Lines 57-82)

```python
def get_ai_question(conversation_history: List[Dict[str, str]]) -> str:
```

**Line 57**: Function to get the next AI response.
- **Parameter**: Full conversation history up to this point
- **Returns**: The AI's question or guess as a string
- **Why separate function**: Encapsulates API call logic, makes it testable

```python
    """
    Get the next question or guess from the AI.
    
    Args:
        conversation_history: List of message dictionaries with role and content
        
    Returns:
        The AI's question or guess as a string
    """
```

**Lines 58-66**: Docstring with parameter and return descriptions.

```python
    try:
```

**Line 67**: Starts error handling block.
- **Why try/except**: API calls can fail (network issues, invalid key, rate limits)
- **Graceful degradation**: We want to show errors to users, not crash the app

```python
        client = get_client()
```

**Line 68**: Gets the OpenAI client.
- **Why call function**: Uses lazy initialization - client created only when needed
- **First call**: Creates client (may raise error if API key missing)
- **Subsequent calls**: Returns existing client instance

```python
        response = client.chat.completions.create(
```

**Line 69**: Makes the API call to OpenAI.
- **`client.chat.completions.create()`**: Method to create a chat completion (conversation)
- **What it does**: Sends conversation history to OpenAI, gets AI's response
- **Async alternative**: Could use async version for better performance, but adds complexity

```python
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency, can switch to gpt-4 if needed
```

**Line 70**: Specifies which model to use.
- **"gpt-4o-mini"**: Smaller, cheaper version of GPT-4
- **Why this model**: 
  - Cost: ~10x cheaper than GPT-4
  - Speed: Faster responses
  - Quality: Sufficient for this use case
- **Trade-off**: Slightly less capable than GPT-4, but adequate for 20 Questions

```python
            messages=conversation_history,
```

**Line 71**: Passes the conversation history.
- **Why full history**: Model needs all previous Q&A to make informed decisions
- **Format**: List of dicts with "role" and "content" keys
- **Token usage**: Each message adds tokens, but 20 questions is well within limits

```python
            temperature=0.7,
```

**Line 72**: Sets the temperature parameter.
- **What is temperature**: Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
- **Why 0.7**: 
  - High enough: Generates varied, creative questions
  - Low enough: Maintains consistency and focus
- **Trade-off**: Lower = more repetitive, Higher = less focused

```python
            max_tokens=150
```

**Line 73**: Limits response length.
- **What it does**: Maximum tokens the model can generate in response
- **Why 150**: 
  - Questions are short (usually 10-30 words)
  - Guesses are single words
  - Prevents overly long responses
- **Token estimate**: ~150 tokens ≈ 100-150 words

```python
        ai_message = response.choices[0].message.content.strip()
```

**Line 76**: Extracts the AI's message from the response.
- **`response.choices[0]`**: API returns a list of choices, we take the first
- **`.message.content`**: The actual text the AI generated
- **`.strip()`**: Removes leading/trailing whitespace
- **Why strip**: Clean up any extra spaces the model might add

```python
        return ai_message
```

**Line 77**: Returns the cleaned message.
- **What gets returned**: The AI's question or guess as a string
- **Used by**: `app.py` to display to user and check for guesses

```python
    except ValueError as e:
        return f"Configuration Error: {str(e)}"
```

**Lines 78-79**: Handles configuration errors (missing API key).
- **Why separate handler**: Configuration errors are different from API errors
- **User-friendly**: Shows clear error message instead of crashing
- **When it happens**: If `get_client()` raises `ValueError` (API key missing)

```python
    except Exception as e:
        return f"Error: {str(e)}. Please check your API key and try again."
```

**Lines 80-81**: Catches all other errors.
- **Why catch-all**: Network errors, API errors, rate limits, etc.
- **Generic message**: Tells user to check API key (common issue)
- **Limitation**: Could be more specific, but covers most cases

### Adding Player Answers (Lines 84-92)

```python
def add_player_answer(conversation_history: List[Dict[str, str]], answer: str) -> None:
```

**Line 84**: Function to add player's answer to history.
- **Parameters**: 
  - `conversation_history`: The list to modify (passed by reference)
  - `answer`: The player's answer string
- **Returns**: `None` (modifies list in place)
- **Why separate function**: Encapsulates the logic, makes code cleaner

```python
    """
    Add the player's answer to the conversation history.
    
    Args:
        conversation_history: List of message dictionaries
        answer: Player's answer ("Yes", "No", "Sometimes", or "Unknown")
    """
```

**Lines 85-91**: Docstring explaining the function.

```python
    conversation_history.append({"role": "user", "content": answer})
```

**Line 92**: Appends the answer to the conversation history.
- **Why append**: Adds to the end of the list (maintains chronological order)
- **`{"role": "user", ...}`**: Marks this as a user message (not AI)
- **Format**: Matches OpenAI's expected message format
- **In-place modification**: Modifies the list passed in (Python lists are mutable)

### Checking for Guesses (Lines 95-146)

This function uses regex to extract guesses from the AI's natural language responses. This is necessary because models don't always follow the structured "GUESS: word" format.

```python
def check_for_guess(message: str) -> Optional[str]:
```

**Line 95**: Function to detect if AI made a guess.
- **Parameter**: The AI's message (could be question or guess)
- **Returns**: The guessed word if found, `None` otherwise
- **Why `Optional[str]`**: Can return either a string (guess found) or `None` (no guess)

```python
    """
    Check if the AI message contains a guess.
    Guesses are in the format "GUESS: [word]" or similar patterns.
    
    Args:
        message: The AI's message
        
    Returns:
        The guessed word if found, None otherwise
    """
```

**Lines 96-105**: Docstring with detailed explanation.

```python
    import re
```

**Line 106**: Imports the `re` module for regex.
- **Why import here**: Only needed in this function, so import locally
- **Alternative**: Could import at top of file, but local import is fine for single-use

```python
    message_lower = message.lower()
```

**Line 108**: Converts message to lowercase.
- **Why lowercase**: Makes regex matching case-insensitive
- **Example**: "GUESS: Elephant" and "guess: elephant" both match
- **Performance**: Single conversion, then all checks use lowercase version

```python
    # Check for explicit "GUESS:" format (case insensitive)
    guess_match = re.search(r'guess\s*:\s*([^\s\.\?!]+)', message_lower)
```

**Line 111**: First regex pattern - looks for "GUESS: word" format.
- **`re.search()`**: Finds first match in the string
- **Pattern breakdown**:
  - `guess`: Literal word "guess"
  - `\s*`: Zero or more whitespace characters (handles "GUESS :" or "GUESS:")
  - `:`: Literal colon
  - `\s*`: More optional whitespace
  - `([^\s\.\?!]+)`: Capture group - one or more characters that aren't whitespace, period, question mark, or exclamation
- **Why `[^\s\.\?!]+`**: Stops at punctuation or end of word (handles "GUESS: elephant." correctly)

```python
    if guess_match:
        guess = guess_match.group(1).strip()
        guess = guess.replace('"', '').replace("'", "").strip()
        if guess and len(guess) > 1:
            return guess
```

**Lines 112-116**: Processes the matched guess.
- **`guess_match.group(1)`**: Gets the first capture group (the word after "GUESS:")
- **`.strip()`**: Removes whitespace
- **`.replace('"', '')`**: Removes double quotes (handles `GUESS: "elephant"`)
- **`.replace("'", "")`**: Removes single quotes (handles `GUESS: 'elephant'`)
- **`len(guess) > 1`**: Filters out single characters (not valid words)
- **Why return early**: If we find a match, return it immediately (no need to check other patterns)

```python
    # Check for "Is it [word]?" pattern (common guess format)
    # Handle both "Is it word?" and "Is it a/an/the word?" patterns
    is_it_match = re.search(r'is\s+it\s+(?:a|an|the\s+)?([^\s\.\?!]+)', message_lower)
```

**Line 120**: Second regex pattern - looks for "Is it word?" format.
- **Why this pattern**: Models often phrase guesses as questions
- **Pattern breakdown**:
  - `is\s+it\s+`: Literal "is it" with required spaces
  - `(?:a|an|the\s+)?`: Non-capturing group - optional article ("a", "an", or "the")
  - `([^\s\.\?!]+)`: Capture group - the actual word
- **Why non-capturing group**: We don't want to capture "a", "an", or "the" as the guess

```python
    if is_it_match:
        guess = is_it_match.group(1).strip()
        guess = guess.replace('"', '').replace("'", "").strip()
        # Filter out common question words and articles
        if guess and len(guess) > 1 and guess not in ['a', 'an', 'the']:
            return guess
```

**Lines 121-126**: Processes "Is it" pattern matches.
- **Similar to first pattern**: Same cleaning logic
- **Additional check**: `guess not in ['a', 'an', 'the']` - filters out articles that might slip through
- **Why needed**: Regex might capture "a" or "an" if pattern doesn't match perfectly

```python
    # Check for other common guess patterns
    guess_patterns = [
        (r"i\s+think\s+it'?s\s+([^\s\.\?!]+)", 1),
        (r"i\s+believe\s+it'?s\s+([^\s\.\?!]+)", 1),
        (r"it\s+must\s+be\s+([^\s\.\?!]+)", 1),
        (r"the\s+word\s+is\s+([^\s\.\?!]+)", 1),
        (r"my\s+guess\s+is\s+([^\s\.\?!]+)", 1),
    ]
```

**Lines 129-135**: Defines additional regex patterns for common phrasings.
- **Why multiple patterns**: Models phrase guesses in many ways
- **List of tuples**: Each tuple is (pattern, capture_group_number)
- **Patterns cover**:
  - "I think it's elephant"
  - "I believe it's elephant"
  - "It must be elephant"
  - "The word is elephant"
  - "My guess is elephant"
- **`it'?s`**: Handles both "it's" and "its" (apostrophe optional)

```python
    for pattern, group_num in guess_patterns:
        match = re.search(pattern, message_lower)
        if match:
            guess = match.group(group_num).strip()
            guess = guess.replace('"', '').replace("'", "").strip()
            # Remove common articles and filter short words
            if guess and len(guess) > 1 and guess not in ['a', 'an', 'the']:
                return guess
```

**Lines 137-144**: Loops through patterns and checks each one.
- **Why loop**: Check multiple patterns until we find a match
- **Early return**: Returns immediately when match found
- **Same cleaning logic**: Consistent processing across all patterns
- **Why `group_num`**: All patterns use group 1, but kept for flexibility

```python
    return None
```

**Line 146**: Returns `None` if no guess found.
- **When**: If the message is just a question, not a guess
- **Used by**: `app.py` to determine if game should continue or end

### Formatting Conversation History (Lines 149-163)

```python
def format_conversation_history(conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
```

**Line 149**: Function to format history for display.
- **Purpose**: Removes system messages (not user-facing)
- **Returns**: Filtered list without system messages
- **Why needed**: System prompt is implementation detail, users don't need to see it

```python
    """
    Format conversation history for display, excluding system messages.
    
    Args:
        conversation_history: Full conversation history
        
    Returns:
        Formatted history without system messages
    """
```

**Lines 150-158**: Docstring explaining the function.

```python
    formatted = []
```

**Line 159**: Creates empty list for filtered messages.
- **Why new list**: Don't modify original (could cause issues)
- **Immutable approach**: Safer than modifying in place

```python
    for msg in conversation_history:
        if msg["role"] != "system":
            formatted.append(msg)
```

**Lines 160-162**: Filters out system messages.
- **Why loop**: Need to check each message
- **`msg["role"] != "system"`**: Keep only user and assistant messages
- **Why exclude system**: System prompt is long and technical, not relevant to users

```python
    return formatted
```

**Line 163**: Returns the filtered list.
- **Used by**: `app.py` to display conversation history to users

---

## Main Application (app.py) - Complete Breakdown

This file handles all user interface and game flow logic. It uses Streamlit's declarative UI framework.

### Module Docstring and Imports (Lines 1-13)

```python
"""
20Q (Twenty Questions) Game
A Streamlit app where the AI tries to guess an English word by asking yes/no questions.
"""
```

**Lines 1-4**: Module docstring describing the application.

```python
import streamlit as st
```

**Line 6**: Imports Streamlit library.
- **Why `as st`**: Common convention, makes code shorter (`st.button` vs `streamlit.button`)
- **What it provides**: All UI components, session state, page config, etc.

```python
from utils import (
    initialize_game,
    get_ai_question,
    add_player_answer,
    check_for_guess,
    format_conversation_history
)
```

**Lines 7-13**: Imports utility functions.
- **Why specific imports**: Only import what we need (cleaner than `from utils import *`)
- **Each function's role**:
  - `initialize_game`: Sets up new game with system prompt
  - `get_ai_question`: Gets AI's next question/guess
  - `add_player_answer`: Adds player response to history
  - `check_for_guess`: Detects if AI made a guess
  - `format_conversation_history`: Prepares history for display

### Page Configuration (Lines 15-20)

```python
# Page configuration
st.set_page_config(
    page_title="20Q Game",
    page_icon="🎮",
    layout="centered"
)
```

**Line 16**: Configures the Streamlit page.
- **Why here**: Must be called before any other Streamlit commands
- **`page_title`**: Sets browser tab title
- **`page_icon`**: Sets emoji icon in browser tab
- **`layout="centered"**: Centers content (vs "wide" for full-width)
- **When it runs**: Every time the page loads/refreshes

### Session State Initialization (Lines 22-34)

Streamlit's `st.session_state` persists data across reruns (when user interacts with the app). We need to initialize all state variables.

```python
# Initialize session state
if "game_active" not in st.session_state:
    st.session_state.game_active = False
```

**Lines 23-24**: Initializes game active flag.
- **Why check `not in`**: Only initialize if it doesn't exist (prevents overwriting on reruns)
- **`game_active`**: Boolean tracking if a game is currently running
- **Why `False` initially**: No game active when app first loads
- **Used for**: Determining what UI to show (welcome screen vs game screen)

```python
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
```

**Lines 25-26**: Initializes conversation history.
- **Why empty list**: No conversation yet
- **What it stores**: List of message dicts with "role" and "content"
- **Grows during game**: Each Q&A pair gets added
- **Why in session state**: Persists across reruns (Streamlit reruns script on each interaction)

```python
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
```

**Lines 27-28**: Initializes question counter.
- **Why 0**: No questions asked yet
- **Tracks**: How many questions AI has asked
- **Used for**: Displaying progress (e.g., "5/20 questions")
- **Why needed**: Enforce 20-question limit

```python
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
```

**Lines 29-30**: Initializes current question storage.
- **Why empty string**: No question yet
- **Stores**: The AI's current question to display
- **Why separate from history**: Easier to access for display

```python
if "ai_guess" not in st.session_state:
    st.session_state.ai_guess = None
```

**Lines 31-32**: Initializes AI guess storage.
- **Why `None`**: No guess made yet
- **Stores**: The word the AI guessed (if any)
- **Used for**: Determining if game ended with a guess

```python
if "game_over" not in st.session_state:
    st.session_state.game_over = False
```

**Lines 33-34**: Initializes game over flag.
- **Why `False`**: Game hasn't ended
- **Tracks**: Whether game has concluded
- **Used for**: Showing game over screen vs active game screen

**Why all these checks?**: Streamlit reruns the entire script on each interaction. Without these checks, we'd reset state on every rerun, losing game progress.

### Start New Game Function (Lines 37-51)

```python
def start_new_game():
    """Initialize a new game."""
```

**Line 37**: Defines function to start a new game.
- **Why a function**: Reusable - called from multiple places (New Game button, Start Game button, Play Again)
- **What it does**: Resets all game state and gets first question

```python
    st.session_state.game_active = True
```

**Line 39**: Sets game as active.
- **Why `True`**: Game is now running
- **Triggers**: UI changes to show game interface instead of welcome screen

```python
    st.session_state.conversation_history = initialize_game()
```

**Line 40**: Initializes conversation with system prompt.
- **Why call `initialize_game()`**: Gets fresh conversation history with system prompt
- **Overwrites**: Previous game's history (starting fresh)
- **What it contains**: System prompt + initial assistant message

```python
    st.session_state.question_count = 0
```

**Line 41**: Resets question counter.
- **Why 0**: Starting fresh game
- **Will increment**: As questions are asked

```python
    st.session_state.current_question = ""
```

**Line 42**: Clears current question.
- **Why empty**: Will be set to first question next
- **Temporary**: Just clearing old value

```python
    st.session_state.ai_guess = None
```

**Line 43**: Clears any previous guess.
- **Why `None`**: No guess yet in new game

```python
    st.session_state.game_over = False
```

**Line 44**: Resets game over flag.
- **Why `False`**: Game is starting, not ending

```python
    # Get the first question
    conversation = st.session_state.conversation_history
    first_question = get_ai_question(conversation)
```

**Lines 46-48**: Gets the first question from AI.
- **Why get first question**: Game should start with AI asking, not waiting
- **`get_ai_question()`**: Calls OpenAI API with initial conversation
- **What happens**: AI receives system prompt and generates first question

```python
    st.session_state.current_question = first_question
```

**Line 49**: Stores the first question.
- **Why store**: Need to display it in UI
- **Separate storage**: Easier access than digging into conversation history

```python
    st.session_state.conversation_history.append({"role": "assistant", "content": first_question})
```

**Line 50**: Adds first question to history.
- **Why append**: Maintains full conversation history
- **`{"role": "assistant", ...}`**: Marks as AI message
- **Why both store and append**: 
  - Store: For easy display
  - Append: For API context on next call

```python
    st.session_state.question_count = 1
```

**Line 51**: Sets question count to 1.
- **Why 1**: First question has been asked
- **Will increment**: As more questions are asked

### Process Answer Function (Lines 54-83)

This function handles the core game loop: player answers, AI responds.

```python
def process_answer(answer: str):
    """Process the player's answer and get the next question."""
```

**Line 54**: Defines function to process player's answer.
- **Parameter**: The answer string ("Yes", "No", "Sometimes", "Unknown")
- **What it does**: Adds answer, gets next question/guess, updates state

```python
    if not st.session_state.game_active or st.session_state.game_over:
        return
```

**Lines 56-57**: Early return if game not active.
- **Why check**: Prevent processing answers when game isn't running
- **Safety check**: Prevents errors if function called incorrectly
- **Why `return`**: Exit early, don't process answer

```python
    # Add player's answer to conversation
    add_player_answer(st.session_state.conversation_history, answer)
```

**Line 60**: Adds answer to conversation history.
- **Why call function**: Encapsulates the logic
- **Modifies in place**: `add_player_answer` appends to the list
- **Format**: Adds as `{"role": "user", "content": answer}`

```python
    # Check if we've exceeded the question limit
    max_questions = 25 if st.session_state.question_count >= 20 else 20
```

**Line 63**: Determines question limit.
- **Why conditional**: Allow 25 questions if we've already asked 20 (grace period)
- **Normal limit**: 20 questions
- **Extended limit**: 25 if we're past 20 (prevents cutting off mid-game)
- **Logic**: If at 20+, allow up to 25. Otherwise, limit is 20.

```python
    if st.session_state.question_count >= max_questions:
        st.session_state.game_over = True
        st.session_state.game_active = False
        return
```

**Lines 65-68**: Ends game if limit reached.
- **Why check**: Enforce question limit
- **`game_over = True`**: Triggers game over UI
- **`game_active = False`**: Stops processing more answers
- **Why `return`**: Don't get another question, game is done

```python
    # Get AI's next question or guess
    next_response = get_ai_question(st.session_state.conversation_history)
```

**Line 71**: Gets AI's response.
- **Why call now**: After adding player's answer, get AI's next move
- **Full history**: Passes entire conversation (AI needs all context)
- **What it returns**: Either a question or a guess

```python
    # Check if AI made a guess
    guess = check_for_guess(next_response)
```

**Line 74**: Checks if response contains a guess.
- **Why check**: Need to know if game should end
- **Returns**: Guessed word if found, `None` if just a question
- **Uses regex**: Parses natural language to extract guess

```python
    if guess:
        st.session_state.ai_guess = guess
        st.session_state.conversation_history.append({"role": "assistant", "content": next_response})
        st.session_state.game_over = True
        st.session_state.game_active = False
```

**Lines 75-79**: Handles case where AI made a guess.
- **`ai_guess = guess`**: Store the guessed word
- **Append to history**: Save the guess message
- **`game_over = True`**: Trigger game over screen
- **`game_active = False`**: Stop processing more answers
- **Game ends**: Player will see guess and confirm if correct

```python
    else:
        st.session_state.current_question = next_response
        st.session_state.conversation_history.append({"role": "assistant", "content": next_response})
        st.session_state.question_count += 1
```

**Lines 80-83**: Handles case where AI asked another question.
- **`current_question = next_response`**: Store for display
- **Append to history**: Maintain full conversation
- **`question_count += 1`**: Increment counter
- **Game continues**: Player will see new question and can answer

### Main UI - Title and Description (Lines 86-88)

```python
# Main UI
st.title("🎮 20Q Game")
st.markdown("Think of an English word, and I'll try to guess it by asking you questions!")
```

**Line 87**: Displays page title.
- **`st.title()`**: Large heading at top of page
- **Emoji**: Visual indicator of game theme

**Line 88**: Displays instructions.
- **`st.markdown()`**: Renders markdown text
- **Purpose**: Brief explanation of how game works
- **User guidance**: Helps users understand what to do

### Game Status Display (Lines 90-100)

```python
# Game status display
col1, col2 = st.columns(2)
```

**Line 91**: Creates two columns for layout.
- **Why columns**: Side-by-side layout (status on left, button on right)
- **`st.columns(2)`**: Creates two equal-width columns
- **Returns**: List of column objects to use as context managers

```python
with col1:
    if st.session_state.game_active:
        st.info(f"**Questions asked:** {st.session_state.question_count}/20")
    else:
        st.info("**Status:** Ready to play")
```

**Lines 92-96**: Displays game status in first column.
- **`with col1:`**: Context manager - everything inside goes in first column
- **Conditional display**: 
  - If game active: Show question count
  - If not active: Show "Ready to play"
- **`st.info()`**: Info box with blue background
- **Why f-string**: Dynamic content based on state

```python
with col2:
    if st.button("New Game", use_container_width=True):
        start_new_game()
```

**Lines 98-100**: New Game button in second column.
- **`with col2:`**: Everything inside goes in second column
- **`st.button()`**: Creates clickable button
- **`use_container_width=True`**: Button fills column width
- **On click**: Calls `start_new_game()` function
- **Note**: Streamlit reruns script when button clicked (triggers `st.rerun()` implicitly)

### Active Game UI (Lines 102-130)

```python
# Game area
if st.session_state.game_active and not st.session_state.game_over:
```

**Line 103**: Condition for showing active game interface.
- **Why both checks**: 
  - `game_active`: Game must be running
  - `not game_over`: Game must not have ended
- **When true**: Show question and answer buttons

```python
    # Display current question
    st.markdown("### 🤔 My Question:")
    st.markdown(f"**{st.session_state.current_question}**")
```

**Lines 104-106**: Displays AI's current question.
- **`###`**: Markdown heading (smaller than title)
- **Emoji**: Visual indicator
- **Bold text**: Makes question stand out
- **Why `current_question`**: Easy access to current question (vs parsing history)

```python
    # Answer buttons
    st.markdown("### 💬 Your Answer:")
    col1, col2, col3, col4 = st.columns(4)
```

**Lines 108-110**: Sets up answer buttons.
- **Heading**: Labels the button section
- **Four columns**: One for each answer option
- **Equal width**: Each button gets 25% of width

```python
    with col1:
        if st.button("✅ Yes", use_container_width=True, type="primary"):
            process_answer("Yes")
            st.rerun()
```

**Lines 112-115**: Yes button.
- **`type="primary"`**: Blue button (stands out as default/positive answer)
- **`use_container_width=True`**: Button fills column
- **On click**: 
  - Calls `process_answer("Yes")` - adds answer, gets next question
  - `st.rerun()` - reruns script to update UI with new question
- **Why `st.rerun()`**: Streamlit needs to rerun to show updated state

```python
    with col2:
        if st.button("❌ No", use_container_width=True):
            process_answer("No")
            st.rerun()
```

**Lines 117-120**: No button.
- **Similar to Yes**: Same pattern, different answer
- **No `type="primary"`**: Regular button (not highlighted)

```python
    with col3:
        if st.button("🤷 Sometimes", use_container_width=True):
            process_answer("Sometimes")
            st.rerun()
```

**Lines 122-125**: Sometimes button.
- **Handles ambiguity**: For questions that don't have clear yes/no
- **Example**: "Is it alive?" for "virus" (depends on definition)

```python
    with col4:
        if st.button("❓ Unknown", use_container_width=True):
            process_answer("Unknown")
            st.rerun()
```

**Lines 127-130**: Unknown button.
- **Handles uncertainty**: When player doesn't know the answer
- **Useful for**: Complex or technical words

### Game Over UI (Lines 132-154)

```python
elif st.session_state.game_over:
```

**Line 132**: Condition for game over screen.
- **When**: Game has ended (either AI guessed or limit reached)

```python
    # Game over - show result
    if st.session_state.ai_guess:
```

**Line 134**: Checks if AI made a guess.
- **Two end scenarios**: AI guessed OR question limit reached
- **This branch**: AI made a guess

```python
        st.success(f"### I think the word is: **{st.session_state.ai_guess}**")
        st.markdown("Was I correct?")
```

**Lines 135-136**: Displays the guess.
- **`st.success()`**: Green success box (positive feedback)
- **Bold guess**: Makes the word stand out
- **Confirmation prompt**: Asks player if guess was correct

```python
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, you got it!", use_container_width=True, type="primary"):
                st.balloons()
                st.session_state.game_active = False
                st.rerun()
```

**Lines 138-143**: Correct guess button.
- **Two columns**: Yes and No buttons side by side
- **`st.balloons()`**: Celebration animation (confetti effect)
- **`game_active = False`**: Reset state
- **`st.rerun()`**: Updates UI (removes buttons, shows ready state)

```python
        with col2:
            if st.button("❌ No, that's not it", use_container_width=True):
                st.info("Thanks for playing! The word was tricky to guess.")
                st.session_state.game_active = False
                st.rerun()
```

**Lines 144-148**: Incorrect guess button.
- **`st.info()`**: Shows message thanking player
- **Resets state**: Same as correct button
- **No balloons**: Less celebratory (AI was wrong)

```python
    else:
        st.warning("### ⏱️ Game Over!")
        st.markdown(f"I couldn't guess the word in {st.session_state.question_count} questions. You win!")
        if st.button("Play Again", use_container_width=True):
            start_new_game()
            st.rerun()
```

**Lines 149-154**: Game over without a guess (AI ran out of questions).
- **`else`**: Executes when `ai_guess` is `None` (no guess was made)
- **`st.warning()`**: Yellow warning box indicating game over
- **Dynamic message**: Shows actual question count used
- **"Play Again" button**: Allows immediate restart without going back to welcome screen
- **`start_new_game()`**: Resets all game state
- **`st.rerun()`**: Refreshes UI to show new game

---

### Welcome Screen (Lines 156-172)

```python
else:
    # Welcome screen
    st.markdown("""
    ### How to Play:
    1. Click **"New Game"** to start
    2. Think of an English word
    3. Answer my questions with:
       - **Yes** ✅
       - **No** ❌
       - **Sometimes** 🤷
       - **Unknown** ❓
    4. I'll try to guess your word in 20 questions!
    """)
    
    if st.button("Start Game", use_container_width=True, type="primary"):
        start_new_game()
        st.rerun()
```

**Lines 156-172**: Initial welcome screen when no game is active.
- **`else`**: Executes when `game_active` is `False` and `game_over` is `False`
- **Triple-quoted string**: Multi-line markdown for instructions
- **Markdown formatting**: Uses `**bold**` and emojis for visual appeal
- **"Start Game" button**: Primary button (blue) to begin
- **`type="primary"`**: Makes button visually prominent
- **Same function**: Uses `start_new_game()` like other entry points

**Why two entry points?** ("New Game" at top and "Start Game" here)
- **"New Game"**: Always visible, allows restarting mid-game
- **"Start Game"**: Only on welcome screen, clearer call-to-action for first-time users

---

### Conversation History Display (Lines 174-190)

```python
# Conversation history
if st.session_state.conversation_history and len(st.session_state.conversation_history) > 1:
    st.markdown("---")
    st.markdown("### Conversation History")
    
    formatted_history = format_conversation_history(st.session_state.conversation_history)
    
    # Display history in reverse order (newest first) or chronological
    for i, msg in enumerate(formatted_history):
        if msg["role"] == "assistant":
            st.markdown(f"**🤖 AI:** {msg['content']}")
        elif msg["role"] == "user":
            st.markdown(f"**👤 You:** {msg['content']}")
        
        # Add separator between Q&A pairs
        if i < len(formatted_history) - 1:
            st.markdown("---")
```

**Lines 174-190**: Displays full conversation history below the game area.

**Line 175**: Conditional display check.
- **`st.session_state.conversation_history`**: Checks if history exists (not `None` or empty)
- **`len(...) > 1`**: Only shows if there's more than just the system prompt
- **Why > 1?**: System message + initial assistant message = 2 minimum

**Line 176**: Horizontal rule separator.

**Line 177**: Section header.

**Line 179**: Format conversation history.
- **`format_conversation_history()`**: Removes system messages (not user-facing)
- **Returns**: Clean list of user/assistant messages only

**Lines 182-186**: Loop through messages.
- **`enumerate()`**: Gets both index and message for separator logic
- **Role checking**: Different formatting for AI vs user
- **Emoji prefixes**: Visual distinction (🤖 for AI, 👤 for user)
- **`msg['content']`**: Extracts the actual message text

**Lines 189-190**: Separator between messages.
- **`i < len(...) - 1`**: Don't add separator after last message
- **Visual clarity**: Makes Q&A pairs easier to distinguish

**Why show history?**
- **Transparency**: Users can see all questions asked
- **Debugging**: Helps identify if AI misunderstood answers
- **User experience**: Some users like reviewing the conversation

---

### Footer (Lines 192-194)

```python
# Footer
st.markdown("---")
st.markdown("Built with Streamlit")
```

**Lines 192-194**: Simple footer.
- **Separator**: Visual break from main content
- **Attribution**: Credits Streamlit framework
- **Minimal**: Doesn't distract from game

---

## Complete Code Flow Diagram

```
App Start
    ↓
Initialize Session State (Lines 23-34)
    ↓
Page Config (Lines 16-20)
    ↓
Display Title & Instructions (Lines 87-88)
    ↓
┌─────────────────────────────────────┐
│  Game State Check                    │
└─────────────────────────────────────┘
    │
    ├─→ Welcome Screen (Lines 156-172)
    │   └─→ User clicks "Start Game"
    │       └─→ start_new_game() (Lines 37-51)
    │
    ├─→ Active Game (Lines 103-130)
    │   ├─→ Display current question
    │   ├─→ User clicks answer button
    │   └─→ process_answer() (Lines 54-83)
    │       ├─→ Add answer to history
    │       ├─→ Check question limit
    │       ├─→ Get AI response
    │       └─→ Check for guess or continue
    │
    └─→ Game Over (Lines 132-154)
        ├─→ AI made guess → Confirm result
        └─→ No guess → Show timeout message
    ↓
Display Conversation History (Lines 174-190)
    ↓
Display Footer (Lines 192-194)
```

---

## Common Questions & Answers

### Q: Why use session state instead of global variables?
**A**: Streamlit reruns the entire script on each interaction. Global variables would reset. Session state persists across reruns, maintaining game state.

### Q: Why lazy client initialization?
**A**: Module-level initialization fails in cloud deployments if the API key isn't set. Lazy initialization provides better error messages and only creates the client when needed.

### Q: Why check `game_active` and `game_over` separately?
**A**: They represent different states:
- `game_active = False, game_over = False`: Welcome screen
- `game_active = True, game_over = False`: Active game
- `game_active = False, game_over = True`: Game ended

### Q: Why `st.rerun()` after every button click?
**A**: Streamlit needs to rerun to update the UI. Without it, the page wouldn't reflect state changes.

### Q: Why extend to 25 questions instead of hard 20?
**A**: Gives AI flexibility if it's close to guessing. Better user experience than strict cutoff.

### Q: Why multiple regex patterns for guess extraction?
**A**: LLMs don't always follow exact formats. Multiple patterns catch various phrasings like "Is it X?", "I think it's X", etc.

### Q: Why `temperature=0.7`?
**A**: Balance between creativity (varied questions) and consistency (stays on topic). Too low = repetitive, too high = random.

### Q: Why `max_tokens=150`?
**A**: Questions should be short. Prevents long-winded responses and saves tokens/cost.

### Q: Why store full conversation history?
**A**: Each API call needs full context. The model uses all previous Q&A to make informed guesses.

### Q: Why separate `utils.py`?
**A**: Separation of concerns:
- `app.py`: UI and user interaction
- `utils.py`: Business logic and API calls
- Easier to test and maintain

---

## Performance Considerations

1. **Token Usage**: Each API call includes full history. For 20 questions, this is ~500-1000 tokens per call, acceptable for this use case.

2. **API Latency**: Each question requires an API call (~1-2 seconds). The UI shows loading state during this time.

3. **Session State Size**: Conversation history grows linearly. For 20 questions, this is minimal memory usage.

4. **Cost Optimization**: Using `gpt-4o-mini` instead of `gpt-4` reduces cost by ~10x while maintaining quality.

---

## Security Considerations

1. **API Key**: Never committed to git (`.gitignore` includes `.env`). Use Streamlit Secrets for cloud deployment.

2. **Input Validation**: User answers are limited to predefined buttons, preventing injection attacks.

3. **Error Handling**: API errors are caught and displayed to users without exposing sensitive details.

---

## Future Enhancement Opportunities

1. **Caching**: Cache common questions/patterns to reduce API calls
2. **Streaming**: Stream AI responses for better UX
3. **Analytics**: Track win rate, average questions needed
4. **Themes**: Different word categories (animals, objects, etc.)
5. **Multiplayer**: Compete with friends
6. **Difficulty Levels**: Adjust AI strategy based on difficulty

---

## Conclusion

This application demonstrates a complete conversational AI interface with proper state management, error handling, and user experience considerations. Every design decision serves a specific purpose in creating a functional, maintainable, and user-friendly game.

The code follows best practices for Streamlit development, OpenAI API integration, and Python programming. Understanding each line helps in debugging, extending, and maintaining the application.