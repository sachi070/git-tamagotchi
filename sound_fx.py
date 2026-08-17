import math
import struct
import io
import os
import threading
import platform
import subprocess
import ctypes

MP3_FILE = os.path.abspath("meow.mp3")

def _generate_meow_wav() -> bytes:
    """Synthesizes a backup sliding meow sound wave in memory."""
    sample_rate = 22050
    duration = 0.38
    total_samples = int(sample_rate * duration)
    buffer = io.BytesIO()

    # WAV Header (PCM 16-bit mono 22050Hz)
    buffer.write(b"RIFF")
    buffer.write(struct.pack("<I", 36 + total_samples * 2))
    buffer.write(b"WAVEfmt ")
    buffer.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buffer.write(b"data")
    buffer.write(struct.pack("<I", total_samples * 2))

    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 600 + 550 * math.sin(math.pi * t)
        amp = math.sin(math.pi * t) ** 0.8
        phase += 2.0 * math.pi * freq / sample_rate
        sample = int(32767.0 * 0.45 * amp * math.sin(phase))
        buffer.write(struct.pack("<h", max(-32767, min(32767, sample))))

    return buffer.getvalue()

def _generate_chime_wav() -> bytes:
    """Synthesizes a clean 4-note victory chime."""
    sample_rate = 22050
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    note_dur = 0.09
    total_samples = int(sample_rate * note_dur * len(notes))
    buffer = io.BytesIO()

    buffer.write(b"RIFF")
    buffer.write(struct.pack("<I", 36 + total_samples * 2))
    buffer.write(b"WAVEfmt ")
    buffer.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buffer.write(b"data")
    buffer.write(struct.pack("<I", total_samples * 2))

    for freq in notes:
        n_samples = int(sample_rate * note_dur)
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            amp = math.sin(math.pi * (1.0 - t)) ** 0.5
            phase += 2.0 * math.pi * freq / sample_rate
            sample = int(32767.0 * 0.4 * amp * math.sin(phase))
            buffer.write(struct.pack("<h", sample))

    return buffer.getvalue()

# Pre-generate in-memory audio buffers
MEOW_BYTES = _generate_meow_wav()
CHIME_BYTES = _generate_chime_wav()

def _play_mp3_windows(file_path: str):
    """Plays an MP3 file on Windows using the native winmm MCI interface."""
    winmm = ctypes.windll.winmm
    # Close any previously open sound alias
    winmm.mciSendStringW("close meow_sound", None, 0, None)
    # Open and play new sound
    cmd_open = f'open "{file_path}" type mpegvideo alias meow_sound'
    winmm.mciSendStringW(cmd_open, None, 0, None)
    winmm.mciSendStringW("play meow_sound from 0", None, 0, None)

def play_meow():
    """Plays meow.mp3 if present; otherwise plays the synthesized meow wave."""
    def _sound():
        if platform.system() == "Windows":
            if os.path.exists(MP3_FILE):
                try:
                    _play_mp3_windows(MP3_FILE)
                    return
                except Exception:
                    pass
            # Fallback to synthesized wave
            try:
                import winsound
                winsound.PlaySound(MEOW_BYTES, winsound.SND_MEMORY | winsound.SND_ASYNC)
            except Exception:
                pass
    threading.Thread(target=_sound, daemon=True).start()

def play_level_up():
    def _sound():
        if platform.system() == "Windows":
            try:
                import winsound
                winsound.PlaySound(CHIME_BYTES, winsound.SND_MEMORY | winsound.SND_ASYNC)
            except Exception:
                pass
    threading.Thread(target=_sound, daemon=True).start()

def notify_desktop(title: str, message: str):
    def _notify():
        if platform.system() == "Windows":
            try:
                ps_script = f'''
                [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");
                $notify = New-Object System.Windows.Forms.NotifyIcon;
                $notify.Icon = [System.Drawing.SystemIcons]::Information;
                $notify.Visible = $true;
                $notify.ShowBalloonTip(3000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info);
                '''
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True)
            except Exception:
                pass
    threading.Thread(target=_notify, daemon=True).start()