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
    config=streaming_config, interim_results=True
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
    def generate_requests():
        while True:
            chunk = audio_queue.get()
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    requests = generate_requests()

    streaming_recognize_responses = client.streaming_recognize(
        config=streaming_config, requests=requests
    )

    for response in streaming_recognize_responses:
        for result in response.results:
            if result.is_final:
                print("Transcript: {}".format(result.alternatives[0].transcript))
            else:
                print("Interim Transcript: {}".format(result.alternatives[0].transcript))
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
