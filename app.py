"""
20Q (Twenty Questions) Game
A Streamlit app where the AI tries to guess an English word by asking yes/no questions.
"""

import streamlit as st
from utils import (
    initialize_game,
    get_ai_question,
    add_player_answer,
    check_for_guess,
    format_conversation_history
)

# Page configuration
st.set_page_config(
    page_title="20Q Game",
    page_icon="❓",
    layout="centered"
)

# Initialize session state
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "ai_guess" not in st.session_state:
    st.session_state.ai_guess = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False


def start_new_game():
    """Initialize a new game."""
    st.session_state.game_active = True
    st.session_state.conversation_history = initialize_game()
    st.session_state.question_count = 0
    st.session_state.current_question = ""
    st.session_state.ai_guess = None
    st.session_state.game_over = False
    
    # Get the first question
    conversation = st.session_state.conversation_history
    first_question = get_ai_question(conversation)
    st.session_state.current_question = first_question
    st.session_state.conversation_history.append({"role": "assistant", "content": first_question})
    st.session_state.question_count = 1


def process_answer(answer: str):
    """Process the player's answer and get the next question."""
    if not st.session_state.game_active or st.session_state.game_over:
        return
    
    # Add player's answer to conversation
    add_player_answer(st.session_state.conversation_history, answer)
    
    # Check if we've exceeded the question limit
    max_questions = 25 if st.session_state.question_count >= 20 else 20
    
    if st.session_state.question_count >= max_questions:
        st.session_state.game_over = True
        st.session_state.game_active = False
        return
    
    # Get AI's next question or guess
    next_response = get_ai_question(st.session_state.conversation_history)
    
    # Check if AI made a guess
    guess = check_for_guess(next_response)
    if guess:
        st.session_state.ai_guess = guess
        st.session_state.conversation_history.append({"role": "assistant", "content": next_response})
        st.session_state.game_over = True
        st.session_state.game_active = False
    else:
        st.session_state.current_question = next_response
        st.session_state.conversation_history.append({"role": "assistant", "content": next_response})
        st.session_state.question_count += 1


# Main UI
st.title("🎮 20Q Game")
st.markdown("Think of an English word, and I'll try to guess it by asking you questions!")

# Game status display
col1, col2 = st.columns(2)
with col1:
    if st.session_state.game_active:
        st.info(f"**Questions asked:** {st.session_state.question_count}/20")
    else:
        st.info("**Status:** Ready to play")

with col2:
    if st.button("🔄 New Game", use_container_width=True):
        start_new_game()

# Game area
if st.session_state.game_active and not st.session_state.game_over:
    # Display current question
    st.markdown("### 🤔 My Question:")
    st.markdown(f"**{st.session_state.current_question}**")
    
    # Answer buttons
    st.markdown("### 💬 Your Answer:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Yes", use_container_width=True, type="primary"):
            process_answer("Yes")
            st.rerun()
    
    with col2:
        if st.button("❌ No", use_container_width=True):
            process_answer("No")
            st.rerun()
    
    with col3:
        if st.button("🤷 Sometimes", use_container_width=True):
            process_answer("Sometimes")
            st.rerun()
    
    with col4:
        if st.button("❓ Unknown", use_container_width=True):
            process_answer("Unknown")
            st.rerun()

elif st.session_state.game_over:
    # Game over - show result
    if st.session_state.ai_guess:
        st.success(f"### 🎯 I think the word is: **{st.session_state.ai_guess}**")
        st.markdown("Was I correct?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, you got it!", use_container_width=True, type="primary"):
                st.balloons()
                st.session_state.game_active = False
                st.rerun()
        with col2:
            if st.button("❌ No, that's not it", use_container_width=True):
                st.info("Thanks for playing! The word was tricky to guess.")
                st.session_state.game_active = False
                st.rerun()
    else:
        st.warning("### ⏱️ Game Over!")
        st.markdown(f"I couldn't guess the word in {st.session_state.question_count} questions. You win!")
        if st.button("🔄 Play Again", use_container_width=True):
            start_new_game()
            st.rerun()

else:
    # Welcome screen
    st.markdown("""
    ### How to Play:
    1. Click **"🔄 New Game"** to start
    2. Think of an English word
    3. Answer my questions with:
       - **Yes** ✅
       - **No** ❌
       - **Sometimes** 🤷
       - **Unknown** ❓
    4. I'll try to guess your word in 20 questions!
    """)
    
    if st.button("🚀 Start Game", use_container_width=True, type="primary"):
        start_new_game()
        st.rerun()

# Conversation history
if st.session_state.conversation_history and len(st.session_state.conversation_history) > 1:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
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

# Footer
st.markdown("---")
st.markdown("Built with Streamlit")

