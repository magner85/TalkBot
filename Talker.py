import subprocess
import parametrs

class Talker:
    def __init__(self, TalkerSet: parametrs.Talker, path :str = 'balcon.exe'):
        self.path = path
        self.Talker_settings = TalkerSet

    def run(self, file: str):
        cmd = [self.path]
        cmd.append('-w'); cmd.append('tmp\\' + file)
        cmd.append('-t'); cmd.append(self.Talker_settings.text.__str__())
        cmd.append('-s'); cmd.append((int)((self.Talker_settings.voice_speed-50)/5).__str__())
        cmd.append('-p'); cmd.append((int)((self.Talker_settings.pitch_voice-50)/5).__str__())
        cmd.append('-v'); cmd.append(self.Talker_settings.volume.__str__())
        cmd.append('-n'); cmd.append(self.Talker_settings.voice)
        subprocess.run(cmd)

    def get_voices(self):
        rez = subprocess.run([self.path, '-l'], stdout=subprocess.PIPE)
        voices = []
        for voice in rez.stdout.decode('utf-8').split("\n")[2:-1]:
            voices.append(voice[2:-1])
        return voices


