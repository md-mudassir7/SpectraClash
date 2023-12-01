from moviepy.video.io.VideoFileClip import VideoFileClip

class AudioExtractor:
    @staticmethod
    def extract_audio(video_path, audio_output_path="temp.wav"):
        try:
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(audio_output_path)
        except Exception as e:
            print(f"Error extracting audio: {e}")

if __name__ == "__main__":
    # Replace 'your_video_file.mp4' with the actual path to your video file
    input_video_path = "your_video_file.mp4"
    audio_output_path = "temp.wav"

    audio_extractor = AudioExtractor()
    audio_extractor.extract_audio(video_path=input_video_path, audio_output_path=audio_output_path)
