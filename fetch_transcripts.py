import sys, datetime
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.request, json, re

# Paste your channel IDs here (UC... format). Names are just labels.
CHANNELS = {
    "Channel 1": "UC7QHSNOKZvbqpXWFv0SiYDQ",
    "Channel 2": "UCvJZEG5x-DVYZKTz--pS39w",
    "Channel 3": "UCBRpqrzuuqE8TZcWw75JSdw",
    "Channel 4": "UCsJxlgjWIOcuEbOJZ591V3Q",
    "Channel 5": "UCSLOw8JrFTBb3qF-p4v0v_w",
    "Channel 4": "UC-Jd5OMOK1zog0KEj7JAz_g",

}

# Only take videos posted within this many hours (skips stale channels)
HOURS_WINDOW = 26  # covers ~1 day; bump to 74 if you want to catch weekly posts on Mon

def latest_video(channel_id):
    # Pull the channel's RSS feed — no API key needed
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    with urllib.request.urlopen(url) as r:
        xml = r.read().decode()
    vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", xml)
    pub = re.search(r"<published>(.*?)</published>", xml)
    if not vid:
        return None, None
    published = datetime.datetime.fromisoformat(pub.group(1))
    return vid.group(1), published

def is_recent(published):
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - published).total_seconds() / 3600 <= HOURS_WINDOW

out = []
for name, cid in CHANNELS.items():
    try:
        vid, published = latest_video(cid)
        if not vid or not is_recent(published):
            continue  # no new video -> skip this channel
        transcript = YouTubeTranscriptApi.get_transcript(vid)
        text = " ".join(seg["text"] for seg in transcript)
        out.append(f"=== {name} (https://youtu.be/{vid}) ===\n{text}\n")
    except Exception as e:
        print(f"Skipped {name}: {e}", file=sys.stderr)

with open("transcripts.txt", "w") as f:
    if out:
        f.write("\n".join(out))
    else:
        f.write("NO_NEW_VIDEOS")

print(f"Wrote {len(out)} transcripts.")
