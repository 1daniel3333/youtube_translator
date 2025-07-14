import os
import google.generativeai as genai
from transcriber import use_url_check_transcript

def use_transcript_get_summary(transcript):
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError('GOOGLE_API_KEY environment variable not set')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""
    請幫我將以下影片逐字稿進行摘要，條列式列出重點。內容如下：
    {transcript}
    """)
    return response.text

def use_url_get_summary(url):
    transcript = use_url_check_transcript(url)
    summary = use_transcript_get_summary(transcript)
    return summary 