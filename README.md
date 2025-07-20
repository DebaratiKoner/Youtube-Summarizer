# Youtube-Summarizer

A FastAPI web application that summarizes YouTube videos using transcripts and Google Gemini AI.

## Features

- Extracts transcript from YouTube videos.
- Summarizes the transcript using Gemini AI.
- Provides a web interface and API endpoints.
- Returns summary in JSON format.

## Requirements

- Python 3.8+
- [FastAPI](https://fastapi.tiangolo.com/)
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Jinja2

## Setup

1. **Clone the repository** and navigate to the project folder.

2. **Install dependencies:**
   ```powershell
   pip install fastapi uvicorn youtube-transcript-api google-generativeai python-dotenv jinja2
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

4. **Run the application:**
   ```powershell
   uvicorn app:app --reload
   ```

5. **Access the web interface:**
   - Open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

- **Web Interface:** Enter a YouTube video URL and get a summarized topic and description.
- **API Endpoints:**
  - `GET /summarize?url=YOUTUBE_URL`  
    Returns summary JSON for the given YouTube video.
  - `POST /summarize
    Accepts JSON body with `url` field. Returns summary JSON.

## File Structure

- `app.py` - Main FastAPI application.
- `index.html` - Web interface template.
- `style.css` - Styles for the web interface.

## Example Response
```json
{
  "topic_name": "Sample Topic",
  "topic_summary": "This is a brief summary of the YouTube video."
}
```

## Notes

- Ensure the YouTube video has transcripts available.
- The Gemini API key is required for summarization.
