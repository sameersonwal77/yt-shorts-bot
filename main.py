import anthropic
import requests
import os
import subprocess
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ============================================
# API KEYS - GitHub Secrets se aayengi
# ============================================
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# ============================================
# STEP 1: Claude se script generate karo
# ============================================
def generate_script():
    print("📝 Claude se script generate ho rahi hai...")
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    topics = [
        "how to manifest your dream life",
        "law of attraction morning routine",
        "raise your vibration instantly",
        "signs your manifestation is coming",
        "how to let go and trust the universe",
        "abundance mindset shift",
        "scripting technique for manifestation",
        "how thoughts create reality",
        "gratitude and manifestation",
        "how to visualize effectively"
    ]
    
    import random
    topic = random.choice(topics)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Write a powerful 55-second YouTube Shorts script about: {topic}
                
Rules:
- Start with a HOOK that grabs attention in first 3 seconds
- Speak directly to viewer (use "you")
- 3 powerful points
- End with "Follow for daily manifestation tips"
- Tone: calm, spiritual, inspiring
- Language: English (US audience)
- No hashtags, no labels, just the script text"""
            }
        ]
    )
    
    script = message.content[0].text
    print(f"✅ Script ready: {script[:100]}...")
    return script, topic

# ============================================
# STEP 2: ElevenLabs se voice banao
# ============================================
def generate_voice(script):
    print("🎙️ Voice generate ho rahi hai...")
    
    # Rachel voice - calm and spiritual
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.7,
            "style": 0.3
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    with open("audio.mp3", "wb") as f:
        f.write(response.content)
    
    print("✅ Audio ready!")
    return "audio.mp3"

# ============================================
# STEP 3: Pexels se background video lo
# ============================================
def get_background_video():
    print("🎬 Background video download ho rahi hai...")
    
    queries = [
        "meditation spiritual universe",
        "galaxy stars cosmic",
        "nature peaceful zen",
        "lotus flower spiritual",
        "sunrise meditation"
    ]
    
    import random
    query = random.choice(queries)
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium",
        "per_page": 10
    }
    
    response = requests.get("https://api.pexels.com/videos/search", 
                           headers=headers, params=params)
    data = response.json()
    
    videos = data.get("videos", [])
    if not videos:
        print("❌ Video nahi mili!")
        return None
    
    video = random.choice(videos[:5])
    
    # Best quality portrait video file lo
    video_files = video.get("video_files", [])
    portrait_files = [f for f in video_files if f.get("quality") in ["hd", "sd"]]
    
    if not portrait_files:
        portrait_files = video_files
    
    video_url = portrait_files[0]["link"]
    
    video_response = requests.get(video_url, stream=True)
    with open("background.mp4", "wb") as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("✅ Background video ready!")
    return "background.mp4"

# ============================================
# STEP 4: FFmpeg se video banao
# ============================================
def create_video(audio_file, video_file, topic):
    print("🎞️ Video ban rahi hai...")
    
    output_file = "final_video.mp4"
    
    # Audio length nikalo
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "json", audio_file
    ], capture_output=True, text=True)
    
    duration = float(json.loads(result.stdout)["format"]["duration"])
    duration = min(duration + 1, 60)  # Max 60 seconds
    
    # Video + Audio combine karo with looping background
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",  # Background video loop karo
        "-i", video_file,
        "-i", audio_file,
        "-t", str(duration),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        output_file
    ]
    
    subprocess.run(cmd, check=True)
    print("✅ Video ready!")
    return output_file

# ============================================
# STEP 5: YouTube pe upload karo
# ============================================
def upload_to_youtube(video_file, topic):
    print("📤 YouTube pe upload ho raha hai...")
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    creds = None
    
    # Token file check karo
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Client secrets file se flow chalao
            client_config = json.loads(os.environ.get("YOUTUBE_CLIENT_SECRET"))
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    
    youtube = build("youtube", "v3", credentials=creds)
    
    # Video metadata
    today = datetime.now().strftime("%B %d, %Y")
    
    body = {
        "snippet": {
            "title": f"✨ {topic.title()} | Law of Attraction | {today}",
            "description": """✨ Welcome to Shift Your Reality!

Daily manifestation tips to help you create the life you deserve.

🔮 Law of Attraction
💫 Manifestation Techniques  
🌟 Mindset Shifts
✨ Spiritual Growth

Follow for daily doses of manifestation energy!

#LawOfAttraction #Manifestation #ShiftYourReality #Spiritual #Mindset #Abundance #Manifest #Motivation""",
            "tags": ["law of attraction", "manifestation", "spiritual", "mindset", 
                    "abundance", "shift your reality", "manifest", "motivation"],
            "categoryId": "22",  # People & Blogs
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_file, 
                           mimetype="video/mp4",
                           resumable=True,
                           chunksize=1024*1024)
    
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload: {int(status.progress() * 100)}%")
    
    print(f"✅ Video uploaded! ID: {response['id']}")
    print(f"🔗 Link: https://youtube.com/shorts/{response['id']}")
    return response['id']

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    print("🚀 Shift Your Reality Bot Starting...")
    print("=" * 50)
    
    try:
        # Step 1: Script
        script, topic = generate_script()
        
        # Step 2: Voice
        audio = generate_voice(script)
        
        # Step 3: Background
        background = get_background_video()
        
        # Step 4: Video
        video = create_video(audio, background, topic)
        
        # Step 5: Upload
        video_id = upload_to_youtube(video, topic)
        
        print("=" * 50)
        print("🎉 SUCCESS! Video uploaded successfully!")
        print(f"🔗 https://youtube.com/shorts/{video_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise e

if __name__ == "__main__":
    main()
