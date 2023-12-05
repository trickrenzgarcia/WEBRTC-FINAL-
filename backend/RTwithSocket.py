from aiohttp import web
import base64
import json
from google.cloud import speech_v1p1beta1 as speech

# Set your Google Cloud service account key
client = speech.SpeechClient.from_service_account_json('key.json')

async def handle_audio(request):
    try:
        data = await request.json()
        audio_data = data.get('audioData')  # Assuming audioData is sent as base64 string

        # Decode base64 audio data (if needed)
        decoded_audio = base64.b64decode(audio_data)  # You may need additional processing

        # Process the audio data (e.g., perform streaming recognition)
        # ...

        # Return a response (if needed)
        return web.json_response({'status': 'success', 'message': 'Audio processed successfully'})

    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

app = web.Application()
app.router.add_post('/process_audio', handle_audio)

if __name__ == '__main__':
    web.run_app(app, port=8765)
