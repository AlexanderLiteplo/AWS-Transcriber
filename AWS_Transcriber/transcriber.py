from flask import Flask, request, jsonify
import whisperx
import boto3
import gc

app = Flask(__name__)

# AWS S3 configuration
s3 = boto3.client('s3', region_name='us-east-1') 
BUCKET_NAME = 'sagemaker-studio-945712132102-m10offqm0g'  # replace with your bucket name
#29QkQJwb5EWSR/5dGbnw4YZMgTGZKQrv2sfb&DA7
#AKASG6DINGR
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    audio_file_key = request.json.get('audio_file_key')
    if not audio_file_key:
        return jsonify({'error': 'No audio file key provided'}), 400

    # Download file from S3
    local_audio_file = 'temp_audio.mp3'
    s3.download_file(BUCKET_NAME, audio_file_key, local_audio_file)

    # Transcription logic
    device = "cuda"
    batch_size = 16
    compute_type = "float16"

    model = whisperx.load_model("large-v3", device, compute_type=compute_type)
    audio = whisperx.load_audio(local_audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    gc.collect()

    # Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    gc.collect()

    # Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=YOUR_HF_TOKEN, device=device)
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    # Cleanup
    del model, model_a, diarize_model
    gc.collect()

    return jsonify(result["segments"])

if __name__ == '__main__':
    app.run(debug=True)