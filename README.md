# NPTEL Auto Answer

A question answering tool for NPTEL courses that uses multiple LLMs to extract and answer questions from images.

## Setup

If you use uv (recommended):
```bash
uv sync
```

Don't forget to add your Groq API key in `.env`:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

### Web Application (Recommended)

Run the Flask web application:
```bash
uv run app.py
```

Then open your browser and navigate to `http://localhost:5000`

Features:
- Search for courses from the Excel file
- Select a course and enter week number
- View questions from images
- Get AI-generated answers
- Navigate between questions (1-10)

### CLI Mode (Legacy)

For backward compatibility, you can still use the CLI:
```bash
uv run main.py
```

This will prompt for a week number and process all 10 questions for the default course (Cloud Computing - noc25_cs107).

## Course List

The course list is loaded from `NPTEL-Sheet.xlsx` in the parent directory. Cloud Computing (noc25_cs107) is automatically included.

## How It Works

1. Extracts text from question images using a multimodal LLM
2. Queries multiple text-to-text LLMs for answers
3. Returns the most common answer(s) from all models

## Debugging

See [DEBUGGING.md](DEBUGGING.md) for detailed information on:
- How to see errors (terminal, browser, console)
- How to use the Debugger PIN
- Common error locations
- Debugging tips and checklist
