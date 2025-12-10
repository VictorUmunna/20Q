# 20Q Game 🎮

A fun and interactive 20 Questions game built with Python, OpenAI API, and Streamlit. The AI tries to guess an English word you're thinking of by asking intelligent yes/no questions.

## Features

- AI-powered question generation using OpenAI GPT
- Smart guessing based on your answers
- Track questions asked (up to 20, with extension to 25 if needed)
- Full conversation history
- Clean and user-friendly Streamlit interface
- Easy game restart functionality

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your OpenAI API key**:
   - Create a `.env` file in the project root directory
   - Add the following line to `.env`:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - Alternatively, you can copy `env_template.txt` to `.env` and edit it:
     ```bash
     copy env_template.txt .env
     ```
     (On macOS/Linux: `cp env_template.txt .env`)

## Running the App

1. **Make sure your virtual environment is activated**

2. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the URL shown in the terminal (usually `http://localhost:8501`)

## Deploying to Streamlit Cloud

1. **Push your code to GitHub** (make sure `.env` is in `.gitignore` - never commit API keys!)

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)** and connect your repository

3. **Set up your OpenAI API key**:
   - In your Streamlit Cloud app dashboard, go to **Settings** → **Secrets**
   - Add the following secret:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - Click **Save**

4. **Deploy your app** - Streamlit Cloud will automatically detect your `app.py` and deploy it

**Note**: The `.env` file is only used for local development. On Streamlit Cloud, use the Secrets feature to securely store your API key.

## How to Play

1. Click **"🔄 New Game"** or **"🚀 Start Game"** to begin
2. Think of an English word (any noun, verb, adjective, etc.)
3. The AI will ask you yes/no questions
4. Answer using:
   - **Yes** ✅ - The answer is yes
   - **No** ❌ - The answer is no
   - **Sometimes** 🤷 - It depends or sometimes true
   - **Unknown** ❓ - You're not sure
5. The AI will try to guess your word within 20 questions
6. If the AI makes a guess, confirm if it's correct!

## Project Structure

```
20Q/
├── app.py              # Main Streamlit application
├── utils.py            # Helper functions for OpenAI API and game logic
├── requirements.txt    # Python dependencies
├── env_template.txt    # Template for environment variables
├── .env                # Your actual environment variables (create this)
└── README.md           # This file
```

## How It Works

- **No Database**: All guessing logic comes from OpenAI's GPT model. The AI learns from your answers dynamically within each game session.
- **Conversation History**: Each question and answer is passed to the API, allowing the AI to build context and make smarter guesses.
- **Smart Guessing**: The AI analyzes patterns in your answers and makes educated guesses when confident.
- **Question Limits**: The game allows up to 20 questions by default, with an extension to 25 if needed.

## Troubleshooting

### API Key Issues
- Make sure your `.env` file exists and contains `OPENAI_API_KEY=your_actual_key`
- Verify your API key is valid and has credits on your OpenAI account
- Check that `python-dotenv` is installed and loading correctly

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're using the correct Python version (3.8+)

### Streamlit Not Starting
- Try running: `python -m streamlit run app.py`
- Check that Streamlit is installed: `pip show streamlit`

## Future Enhancements

Potential features for future versions:
- 🎯 Hint system
- 📊 Scoreboard or game history
- 🎨 Themes (animals, objects, movies)
- 🌍 Multiple language support
- 🏆 Difficulty levels

## License

This project is open source and available for personal and educational use.

## Credits

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenAI API](https://openai.com/api/) - AI question generation
- [Python](https://www.python.org/) - Programming language

---

Enjoy playing 20Q! 🎉

