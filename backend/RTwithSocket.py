import asyncio
import websockets
import queue
import threading
import pyaudio
from google.cloud import speech_v1p1beta1 as speech

# Set your Google Cloud service account key
client = speech.SpeechClient.from_service_account_json('key.json')

# ... (The rest of your speech recognition configurations)

# Queue to store audio chunks
audio_queue = queue.Queue()

# Function to process audio stream
def audio_callback(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return None, pyaudio.paContinue

# Function to perform streaming recognition
async def handle_audio(websocket, path):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms chunks

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=audio_callback)

    print("Listening...")

    try:
        def streaming_recognize():
            streaming_recognize_requests = (
                speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in iter(lambda: audio_queue.get(), None)
            )

            responses = client.streaming_recognize(
                config=streaming_config, requests=streaming_recognize_requests
            )

            for response in responses:
                # Process the responses and send results through the WebSocket connection
                for result in response.results:
                    if result.is_final:  # Send final transcriptions to the client
                        transcript = result.alternatives[0].transcript
                        await websocket.send(transcript)

        streaming_thread = threading.Thread(target=streaming_recognize)
        streaming_thread.start()

        while streaming_thread.is_alive():
            pass  # Perform other tasks while waiting for streaming to finish

    except Exception as e:
        print(f"Error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

start_server = websockets.serve(handle_audio, 'localhost', 8765)  # Replace 'localhost' with your server IP

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()