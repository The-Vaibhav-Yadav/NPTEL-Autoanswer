# Debugging Guide for NPTEL Auto Answer

## How to See Errors

### 1. **Terminal/Console Output**
When you run the Flask app with `uv run app.py`, all errors and logs appear in your terminal:

```bash
cd NPTEL-Autoanswer
uv run app.py
```

**What you'll see:**
- Server startup messages
- Request logs (GET/POST requests)
- Error tracebacks with full stack traces
- Debugger PIN (when an error occurs)

### 2. **Browser Error Pages**
When `debug=True`, Flask shows detailed error pages in your browser:
- **Full stack trace** showing where the error occurred
- **Interactive debugger** - click on any line number to see the code
- **Console output** showing variable values at the time of error

### 3. **Browser Developer Console**
Open browser DevTools (F12 or Cmd+Option+I) to see:
- JavaScript errors in the Console tab
- Network errors in the Network tab
- API response errors

## How to Use the Debugger PIN

### Step 1: Find the PIN
When an error occurs, Flask prints a **Debugger PIN** in your terminal:

```
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

### Step 2: Use the PIN
1. **Error occurs** → Flask shows error page in browser
2. **Click on any line number** in the error traceback
3. **Enter the PIN** when prompted
4. **Interactive console opens** → You can:
   - Inspect variables
   - Execute Python code
   - Debug the issue in real-time

### Example:
```
Traceback (most recent call last):
  File "app.py", line 142, in get_all_questions_answers
    answers = process_image_question(image_url)
  File "main.py", line 88, in process_image_question
    extracted_text = text_extraction_completion.choices[0].message.content
IndexError: list index out of range

[Click on line 88 to open debugger]
→ Enter PIN: 123-456-789
→ Now you can inspect: image_url, text_extraction_completion, etc.
```

## Common Error Locations

### Backend Errors (Python)
- **Terminal**: Full Python traceback
- **Browser**: Error page with stack trace
- **Check**: `app.py` and `main.py` files

### Frontend Errors (JavaScript)
- **Browser Console**: Open DevTools (F12) → Console tab
- **Network Tab**: See failed API requests
- **Check**: `templates/index.html` JavaScript code

### API Errors
- **Browser Network Tab**: See request/response details
- **Terminal**: Backend error logs
- **Check**: API endpoint responses in browser DevTools

## Tips for Debugging

1. **Always check the terminal first** - Most errors appear there
2. **Use browser DevTools** - Network tab shows API errors
3. **Check the error message** - It usually tells you what's wrong
4. **Look at the stack trace** - Shows exactly where the error occurred
5. **Use print statements** - Add `print()` to see variable values

## Example: Adding Debug Logging

```python
# In app.py, add logging
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/questions', methods=['POST'])
def get_all_questions_answers():
    data = request.json
    logging.debug(f"Received data: {data}")  # See this in terminal
    # ... rest of code
```

## Quick Debug Checklist

- [ ] Check terminal for error messages
- [ ] Check browser console (F12) for JavaScript errors
- [ ] Check browser Network tab for API errors
- [ ] Look at the error page in browser (if debug=True)
- [ ] Use the Debugger PIN if you see it in terminal
- [ ] Check `.env` file for missing API keys
- [ ] Verify Excel file path is correct

