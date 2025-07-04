
import os
# from moviepy.editor import AudioFileClip
from moviepy import *
import yt_dlp
import subprocess

cha_data = {
    "url": "https://www.youtube.com/watch?v=SllWhm9YHHI", 
    "start_time": "00:02:00", 
    "duration": "8", 
    "out_file": "voices/fpt_cha_sample.wav"
}
atu_data = {
    "url": "https://www.youtube.com/watch?v=ZgEeCIMaszw", 
    "start_time": "00:01:08", 
    "duration": "8", 
    "out_file": "voices/fpt_atu_sample.wav"
}

def download_audio_segment(youtube_url, start_time, duration, output_file="sample.wav"):
    # Use yt-dlp to stream audio, pipe it into ffmpeg to cut segment
    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "wav",
        "--external-downloader", "ffmpeg",
        "--external-downloader-args",
        f"ffmpeg_i:-ss {start_time} -t {duration}",
        youtube_url,
        "-o", output_file
    ]

    print("Running command:", " ".join(command))
    subprocess.run(command)

# === Example Usage ===
if __name__ == "__main__":
    # download_audio_segment(cha_data["url"], cha_data["start_time"], cha_data["duration"], cha_data["out_file"])
    download_audio_segment(atu_data["url"], atu_data["start_time"], atu_data["duration"], atu_data["out_file"])
 