# AugmentedSpeechTranslator
from vpipe.core.pipeline import VpComposite
from .speech_translator import SpeechTranslator
from vpipe.capsules.audio.audio_queue_player import VpAudioQueuePlayer
from vpipe.capsules.audio.audio_mixer import VpAudiopMixer
from vpipe.core.fork import VpFork



class AugmentedSpeechTranslator(VpComposite):
    """
    (in) → voice translator → audio queue player → mixer → (out)
        ----------------------------------------→
    (voice translator/asr_script) → script writer
    (voice translator/tran_script) → translated script writer
    """
    def __init__(self, name=None, src_lang='en', dest_lang='vi'):
        super().__init__(name)
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.build()

    def build(self):
        src = VpFork(name="src-fork")
        src1 = src.fork()
        src2 = src.fork()

        speech_translator = SpeechTranslator(name="st",
                                             src_lang=self.src_lang, dest_lang=self.dest_lang)
        audio_queue_player = VpAudioQueuePlayer(name="audio-queue-player")
        src1 >> speech_translator >> audio_queue_player

        mixer = VpAudiopMixer(name="audio-mixer")
        mixer.add_input("src")
        mixer.add_input("tts")
        mixer.get_input("src").set_property('volume', 0.5)

        src2 >> mixer.get_input("src")
        audio_queue_player >> mixer.get_input("tts")
        
        self.expose_input("in", src.get_input("in"))
        self.expose_output("out", mixer.get_output("out"))
        self.expose_output("asr_script", speech_translator.get_output("asr_script"))
        self.expose_output("tran_script", speech_translator.get_output("tran_script"))

        self.adds(
            src,
            speech_translator,
            audio_queue_player,
            mixer
        )

    async def set_prop(self, prop, value):
        match prop:
            case 'src-lang' | 'dest-lang' | 'asr-enable':
                await self.get_capsule("st").set_prop(prop, value)
            case 'tts-enable':
                # immediately mute the TTS output if disabled
                audio_mixer = self.get_capsule("audio-mixer")
                audio_mixer.get_input("tts").set_property("mute", not value)
                # set the TTS enable property in the speech translator
                await self.get_capsule("st").set_prop("tts-enable", value)
            case 'src-volume':
                self.get_capsule("audio-mixer").get_input("src").set_property('volume', value)
            case 'tts-volume':
                self.get_capsule("audio-mixer").get_input("tts").set_property('volume', value)
            case 'tts-speed':
                audio_queue_player = self.get_capsule("audio-queue-player")
                await audio_queue_player.set_prop("speed", value)
            case _:
                raise ValueError(f"Unknown property: {prop}")
            