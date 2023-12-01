import os
import sys
import speech_recognition as sr
from pydub import AudioSegment
import ffmpeg
from extract_audio import AudioExtractor

class HighlightReelGenerator:
    def __init__(self, audio_path, video_path, output_path, threshold_duration=5, threshold_confidence=0.7):
        self.audio_path = audio_path
        self.video_path = video_path
        self.output_path = output_path
        self.threshold_duration = threshold_duration
        self.threshold_confidence = threshold_confidence
        self.segments = []

    def analyze_audio(self, audio_file_path):
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return ""

    def generate_highlight_segments(self):
        audio = AudioSegment.from_wav(self.audio_path)
        duration = len(audio)

        start_time = 0
        while start_time < duration:
            end_time = start_time + self.threshold_duration * 1000
            if end_time > duration:
                end_time = duration

            segment = audio[start_time:end_time]
            segment.export("temp.wav", format="wav")

            transcription = self.analyze_audio("temp.wav")
            os.remove("temp.wav")

            if transcription and segment.duration_seconds >= self.threshold_duration:
                print(f"Segment found at {start_time} - {end_time}")
                self.segments.append((start_time / 1000, end_time / 1000, transcription))

            start_time += self.threshold_duration * 1000

    def combine_segments_to_video(self):
        input_files = []

        for i, segment in enumerate(self.segments):
            segment_file = f"segment_{i}.mp4"
            ffmpeg.input(self.video_path, ss=segment[0], t=segment[1] - segment[0]).output(segment_file).run(
                overwrite_output=True)
            input_files.append(segment_file)

        if len(input_files) > 0:
            # Ensure an even number of input streams for concatenation
            if len(input_files) % 2 != 0:
                input_files.append(input_files[-1])  # Duplicate the last file to make it even

            # Concatenate valid input streams
            ffmpeg.concat(*[ffmpeg.input(file) for file in input_files], v=1, a=1).output(self.output_path).run(
                overwrite_output=True)

            # Clean up temporary segment files
            for file in input_files:
                os.remove(file)
        else:
            print("Error: No valid segments for concatenation.")

    def generate_highlight_reel(self):
        audio = AudioSegment.from_wav(self.audio_path)
        duration = len(audio)

        self.generate_highlight_segments()

        # Combine segments from the last few seconds
        last_few_seconds = 10  # Change this to the desired duration
        last_segment_start = max(0, duration - last_few_seconds * 1000)
        last_segment = audio[last_segment_start:duration]
        last_segment.export("last_segment.wav", format="wav")
        last_transcription = self.analyze_audio("last_segment.wav")
        os.remove("last_segment.wav")

        if last_transcription:
            print(f"Last segment found at {last_segment_start} - {duration}")
            self.segments.append((last_segment_start / 1000, duration / 1000, last_transcription))

        self.combine_segments_to_video()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python highlight_generator.py input_video.mp4 output_highlight_reel.mp4")
        sys.exit(1)

    input_video_path = sys.argv[1]
    output_reel_path = sys.argv[2]

    audio_output_path = "temp.wav"
    audio_extractor = AudioExtractor()
    audio_extractor.extract_audio(video_path=input_video_path, audio_output_path=audio_output_path)

    highlight_generator = HighlightReelGenerator(
        audio_path=audio_output_path,
        video_path=input_video_path,
        output_path=output_reel_path
    )
    highlight_generator.generate_highlight_reel()
