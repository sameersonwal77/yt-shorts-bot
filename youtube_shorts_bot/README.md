# 🚀 Shift Your Reality - YouTube Shorts Bot

## Setup Guide (Laptop Pe Karo)

### Step 1: Files Upload Karo GitHub Pe
1. github.com pe login karo (sameersonwal77)
2. New repository banao - naam: `yt-shorts-bot`
3. `main.py` upload karo
4. `.github/workflows/daily_upload.yml` upload karo

### Step 2: Secrets Add Karo
GitHub repo mein jao:
Settings → Secrets → Actions → New secret

Ye 4 secrets daalo:
- `CLAUDE_API_KEY` = tumhari Claude key
- `ELEVENLABS_API_KEY` = tumhari ElevenLabs key  
- `PEXELS_API_KEY` = tumhari Pexels key
- `YOUTUBE_CLIENT_SECRET` = JSON file ka content

### Step 3: YouTube Auth (Ek Baar)
Pehli baar manually run karna hoga YouTube login ke liye.
Main guide karunga jab laptop pe ho!

### Step 4: Test Karo
Actions tab mein jao → Run workflow → Dekho kaise chalta hai!

---
Roz subah 9 AM IST pe automatically upload hoga! ✅
