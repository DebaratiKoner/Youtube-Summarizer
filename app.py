from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

import os
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Form

import json
import re

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")
templates = Jinja2Templates(directory=".")

load_dotenv()

# Function to get transcript from YouTube video
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = "\n".join([f"{entry['start']}s: {entry['text']}" for entry in transcript])
        return text
    except Exception as e:
        print("Error fetching transcript:", e)
        return None

# Function to send transcript to Gemini and get summary
def summarize_transcript(transcript_text):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""based on the above youtube transcript return me a brief summary of the topic in below json format only:
{
\"topic_name\":\"name of topic\",
\"topic_summary\":\"summary of topic\"
}"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=transcript_text),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        response_mime_type="text/plain",
    )

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents,
        config=generate_content_config,
    )
    
    print(response.text)
    return response.text

# Function to extract video ID from URL
def extract_youtube_id(url):
    """Extract YouTube video ID from a URL."""
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com/watch?v=" in url:
        return url.split("v=")[-1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube URL format")


def extract_json_from_response(response: str):
    """
    Extracts and returns the JSON object from a Gemini-style response string.
    """
    try:
        # Step 1: Extract content between ```json and ```
        match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # fallback if there's no ```json ... ```
            json_str = response.strip()

        # Step 2: Load the string into a Python dict
        # json.loads() handles the escaped quotes
        return json.loads(json_str)
    
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        return None


# Main logic
def main():
    # Replace with actual YouTube video ID
    video_id = extract_youtube_id(url="https://www.youtube.com/watch?v=2MFMwvJd12k")

    transcript_text = get_transcript(video_id)

    if transcript_text:
        summarize_transcript(transcript_text) 

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def summarize_from_form(request: Request, url: str = Form(...)):
    try:
        video_id = extract_youtube_id(url)
        transcript_text = get_transcript(video_id)

        if transcript_text:
            summary = summarize_transcript(transcript_text)
            json_data = extract_json_from_response(summary)
            return templates.TemplateResponse("index.html", {
                "request": request,
                "summary": json_data
            })
        else:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "summary": {"topic_name": "N/A", "topic_summary": "Transcript not available."}
            })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "summary": {"topic_name": "Error", "topic_summary": "Failed to summarize video."}
        })

  

@app.get("/summarize")
def summarize_youtube_video(url: str):
    """
    Endpoint to summarize a YouTube video given its URL.
    """
    try:
        video_id = extract_youtube_id(url)
        transcript_text = get_transcript(video_id)

        if transcript_text:
            summary = summarize_transcript(transcript_text)
            print("Summary ", summary)
            return extract_json_from_response(summary)
        else:
            return {"error": "Transcript not available for this video."}
    except Exception as e:
        print("Error summarizing video:", e)
        return {"error": "Failed to summarize video."}
    
from fastapi import Body

@app.post("/summarize")
async def summarize_youtube_video_post(url: str = Body(...)):
    try:
        video_id = extract_youtube_id(url)
        transcript_text = get_transcript(video_id)

        if transcript_text:
            summary = summarize_transcript(transcript_text)
            return extract_json_from_response(summary)
        else:
            return {"error": "Transcript not available for this video."}
    except Exception as e:
        print("Error:", e)
        return {"error": "Failed to summarize video."}


