import subprocess
import os
import whisper

def use_url_check_transcript(youtube_url):
    print("用 Whisper 分析音訊...")
    cookies_option = ''
    if os.path.exists('cookies.txt'):
        cookies_option = '--cookies cookies.txt '
    subprocess.run(f'yt-dlp {cookies_option}-f bestaudio --extract-audio --audio-format mp3 -o "audio.%(ext)s" "{youtube_url}"', shell=True)
    audio_file = None
    for file in os.listdir():
        if file.endswith(".mp3"):
            audio_file = file
            break
    model = whisper.load_model("small")  # 可改 tiny / base / medium
    result = model.transcribe(audio_file)
    transcript = result["text"]
    # 刪除音訊檔案
    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)
    return transcript 