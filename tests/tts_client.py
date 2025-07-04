import asyncio
import websockets
import json
import soundfile as sf
import io
import os
import numpy as np
import base64
import sounddevice as sd 

SERVER_URL = "ws://localhost:8765"  # Change if needed

def load_wav_file_as_base64(path):
    with open(path, "rb") as f:
        wav_bytes = f.read()
    return base64.b64encode(wav_bytes).decode("utf-8")

async def send_tts_request(text, lang="vi", speaker_id=None, wav_path=None, save_path="output.wav"):
    async with websockets.connect(SERVER_URL, ping_timeout=None, max_size=None) as websocket:
        print("[Client] Connected to server.")

        payload = {
            "lang": lang,
            "text": text,
        }

        if speaker_id:
            payload["speaker_id"] = speaker_id

        if wav_path: 
            samples, sr = sf.read(wav_path, dtype="int16") 
            payload["wav_bytes"] = load_wav_file_as_base64(wav_path)
                        
        # Send JSON payload
        await websocket.send(json.dumps(payload))
        print(f"[Client] Sent request {payload['lang']} {payload['text']}")

        # Receive response
        response = await websocket.recv()

        if isinstance(response, bytes):
            # Treat as audio
            audio_np, sr = sf.read(io.BytesIO(response), dtype='int16')
            print(f"[CLIENT] Playing audio... (Sample rate: {sr}, Shape: {audio_np.shape})")
            sd.play(audio_np, samplerate=sr)
            sd.wait()
            sf.write(str(save_path), audio_np.squeeze(), samplerate=16000)
            return audio_np
        elif isinstance(response, str):
            # Probably an error message from server
            try:
                data = json.loads(response)
                if "error" in data:
                    print("[SERVER ERROR]", data["error"])
                else:
                    print("[ERROR] Unknown response:", data)
            except Exception as e:
                print("[ERROR] Failed to parse server message:", response)
            return np.zeros(16000, dtype=np.int16)

text_ja = "アクティビティ モニターでは、プロセスのリストを階層的に表示して、ターミナルから開始されたプロセスを簡単に見つけることができます。"
text_en = "In Activity Monitor, you can view the list of processes hierarchically, to easily find any processes started from Terminal."
text_vi = "Trong Activity Monitor, bạn có thể xem danh sách các tiến trình theo thứ bậc để dễ dàng tìm thấy bất kỳ tiến trình nào được bắt đầu từ Terminal."


def main(): 
    text = text_vi
    lang = "vi"
    speaker_id = "user_789"
    wav_name = "fpt_atu_sample.wav"
    wav_path = os.path.join("tests", "voices", wav_name)
    print(wav_path)
    save_path = f"test_outputs/{speaker_id}_{wav_name}_{lang}.wav"
    
    asyncio.run(send_tts_request(
        text=text,
        lang=lang,
        speaker_id=speaker_id, 
        wav_path=wav_path,
        save_path=save_path
    ))
    
if __name__ == "__main__":
    main()