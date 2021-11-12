class Talker:
    def __init__(self):
        self.text = ''
        self.volume = 80
        self.pitch_voice = 50
        self.voice_speed = 50
        self.voice = 'Microsoft Irina Desktop'

    def set_par(self, par:str, value:int):
        if par == 'volume':
            self.volume = value
            return
        if par == 'pitch_voice':
            self.pitch_voice = value
            return
        if par == 'voice_speed':
            self.voice_speed = value
            return




