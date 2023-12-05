import pyaudio
import queue
from google.cloud import speech_v1p1beta1 as speech

# Set your Google Cloud service account key
client = speech.SpeechClient.from_service_account_json('key.json')

# Configuration for streaming
streaming_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='fil-PH',
    enable_automatic_punctuation=True,
    use_enhanced=True,
    model="default",

)

streaming_config = speech.StreamingRecognitionConfig(
    config=streaming_config, interim_results=False 
     # Set interim_results to False
)

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks

# Queue to store audio chunks
audio_queue = queue.Queue()

# Function to process audio stream
def audio_callback(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return None, pyaudio.paContinue

# Start audio stream
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=audio_callback)

print("Listening...")

try:
    streaming_recognize_requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk)
        for chunk in iter(lambda: audio_queue.get(), None)
    )

    streaming_recognize_response = client.streaming_recognize(
        config=streaming_config, requests=streaming_recognize_requests
    )

    for response in streaming_recognize_response:
        for result in response.results:
            if result.is_final:  # Print only final transcriptions
                print("Transcript: {}".format(result.alternatives[0].transcript))
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
