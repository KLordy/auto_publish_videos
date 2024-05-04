import whisper


def whisper_model(audio_path):
    model = whisper.load_model("large")
    options = {
        "language": "Mandarin"
    }
    # result = model.transcribe('/Users/zhonghao/PycharmProjects/video_ai/output/audio/origin_audio.mp3', **options)
    result = model.transcribe(audio_path, **options)
    return result


if __name__ == '__main__':
    model = whisper.load_model("medium")
    audio = whisper.load_audio(
        '/Users/zhonghao/PycharmProjects/video_ai/tasks/util/Polar bear physics #science #sciencefacts.mp3')
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    print(result.text)
