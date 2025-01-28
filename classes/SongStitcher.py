from pydub import AudioSegment

from utils.utils import convert_osu_time_to_ms

class SongStitcher:
    def __init__(self, diff_name):
        self.diff_name = diff_name

        self.combined_audio: AudioSegment = AudioSegment.silent(duration=0)
        self.break_time: AudioSegment = AudioSegment.silent(duration=5000)

        self.cur_song_true_start_time = 0
        self.cur_song_fade_in_start_time = 0
        self.cur_song_true_end_time = 0
        self.cur_song_fade_out_end_time = 0
        self.offset = 0

    def get_smooth_start_time(self, audio: AudioSegment, start_time: int) -> int:
        start_time = convert_osu_time_to_ms(start_time)
        new_start_time = max(0, start_time - 2000)
        diff = abs(new_start_time - start_time)
        
        return (new_start_time, diff)

    def get_smooth_end_time(self, audio: AudioSegment, end_time: int) -> tuple[int, int]:
        end_time = convert_osu_time_to_ms(end_time)
        new_end_time = min(len(audio), end_time + 2000)
        diff = abs(new_end_time - end_time)

        return (new_end_time, diff)

    def stitch(self, song_path: str, start_time: int, end_time: int):
        self.offset = len(self.combined_audio)

        audio: AudioSegment = AudioSegment.from_file(song_path)
        
        start_time, start_diff = self.get_smooth_start_time(audio, start_time)
        end_time, end_diff = self.get_smooth_end_time(audio, end_time)

        segment = audio[start_time:end_time].fade_in(duration=start_diff).fade_out(duration=end_diff)

        self.combined_audio = self.combined_audio + segment + self.break_time
        self.cur_song_fade_in_start_time = start_time
        self.cur_song_true_start_time = start_time + start_diff
        self.cur_song_fade_out_end_time = end_time
        self.cur_song_true_end_time = end_time - end_diff

    def export(self):
        self.combined_audio.export(f"testdan/final_{self.diff_name}.mp3", format="mp3")

    def get_true_start_time(self) -> int:
        return self.cur_song_true_start_time
    
    def get_fade_in_start_time(self) -> int:
        return self.cur_song_fade_in_start_time
    
    def get_true_end_time(self) -> int:
        return self.cur_song_true_end_time
    
    def get_fade_out_end_time(self) -> int:
        return self.cur_song_fade_out_end_time

    def get_offset(self) -> int:
        return self.offset