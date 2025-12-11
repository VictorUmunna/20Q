# LinkedIn Post

Just wrapped up building a 20 Questions game using GPT-4o-mini and Streamlit. It's a simple concept, but the implementation surfaced some interesting challenges around conversational AI applications.

The core architecture is straightforward: maintain conversation history in session state, pass the full context to the API on each turn, and let the model handle both question generation and guessing logic. No database needed—the model's context window does the heavy lifting.

A few observations from the build:

**Prompt engineering for structured outputs**: I instructed the model to format guesses as "GUESS: word", but language models don't always follow exact formats. The model would sometimes phrase guesses naturally like "Is it elephant?" instead of the structured format. I handled this by adding regex patterns to extract guesses from multiple phrasings. The takeaway: even with explicit instructions, you need flexible parsing logic because models will vary their output phrasing.

**Temperature tuning**: Settled on 0.7—high enough for varied, strategic questions, but low enough to maintain consistency. Too low and questions become repetitive; too high and the model loses focus.

**Cost vs. capability trade-offs**: Using gpt-4o-mini instead of gpt-4 keeps API costs reasonable for a demo app while still delivering solid performance. The model handles the reasoning well enough that the quality difference isn't noticeable for this use case.

**Context management**: Each API call includes the full conversation history. For a 20-question game, this stays well within token limits, but it's a reminder to monitor context growth in longer conversations.

The app works well, but the process revealed something important: even simple conversational interfaces require careful decisions across multiple areas. You need to manage state properly, design prompts that guide the model effectively, parse outputs that don't always match your expectations, and configure deployments that differ from local development. It's a good reminder that simple applications can expose complex design challenges—the constraints of production environments often surface issues that don't appear during local testing.

Built with Python, OpenAI API, and Streamlit. Deployed on Streamlit Cloud.

