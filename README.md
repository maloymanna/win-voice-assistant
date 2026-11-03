# Windows Voice Assistant

A local, CPU-only voice assistant for Windows 11. Double-tap **Right Ctrl** to record a voice command. The assistant transcribes it with parakeet.cpp / whisper.cpp, matches the intent against a flat YAML configuration, executes the action (open apps, navigate Edge, toggle Focus Assist, take a screenshot, etc.), and speaks the response back via Piper TTS.

No cloud services, no GPU, no Python LLM dependency at runtime.

## Architecture Overview

Right Ctrl (double-tap) -> record_audio() (5s configurable via sounddevice) -> parakeet-cli (--vad --vad-model silero-vad-f16.gguf) -> detect_intent() (commands.yaml: commands / aliases / workflows / exit) -> execute() (subprocess shell or Python marker for screenshot) -> speak_text(response) via Piper TTS (if speak_responses: true) -> notify(response) Windows toast notification.

The tray icon flips between idle and listening. The config.json controls all paths and the record_seconds / speak_responses flags.

## Prerequisites

You need Git, a few downloaded binaries/models, and Python dependencies. All commands below assume Git Bash or PowerShell 7 on Windows 11.

### 1. parakeet.cpp (pre-built binary with VAD support)

Download the v0.6.1 Windows CPU x64 pre-built package, which includes the standalone Silero VAD API:
```bash 
wget https://github.com/mudler/parakeet.cpp/releases/download/v0.6.1/parakeet-v0.6.1-bin-win-cpu-x64.zip
-O parakeet-v0.6.1.zip
unzip parakeet-v0.6.1.zip -d C:/Tools/parakeet/
```
The binary is at `C:/Tools/parakeet/parakeet-cli.exe`. Verify VAD support is present:

`C:/Tools/parakeet/parakeet-cli.exe transcribe --help`

The output should list `--vad` and `--vad-model`. If those flags are missing, fall back to building from `master` (see Troubleshooting).

### 2. GGUF models

Download both files from the mudler/parakeet-cpp-gguf HuggingFace repo:

- tdt_ctc-110m-q8_0.gguf (177.8 MB) — English ASR, hybrid TDT+CTC, WER parity with NeMo
- silero-vad-f16.gguf (~1.3 MB) — Voice Activity Detection for chunking long audio

```bash
    mkdir -p C:/Tools/parakeet/models
    wget https://huggingface.co/mudler/parakeet-cpp-gguf/resolve/main/tdt_ctc-110m-q8_0.gguf \
      -O C:/Tools/parakeet/models/tdt_ctc-110m-q8_0.gguf
    wget https://huggingface.co/mudler/parakeet-cpp-gguf/resolve/main/silero-vad-f16.gguf \
      -O C:/Tools/parakeet/models/silero-vad-f16.gguf
```

### 3. Piper TTS (Windows build + voice)

Download the official Windows binary from the Rhasspy Piper releases page:

    https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip

Unzip to C:/Tools/piper/. The binary is piper.exe.

Download the en_US-lessac-medium voice:

    mkdir -p C:/Tools/piper/voices
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
      -O C:/Tools/piper/voices/en_US-lessac-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json \
      -O C:/Tools/piper/voices/en_US-lessac-medium.onnx.json

Update config.json:

    "piper_exe": "C:/Tools/piper/piper.exe",
    "piper_model": "C:/Tools/piper/voices/en_US-lessac-medium.onnx"

### 4. Python dependencies

    pip install PySide6 keyboard sounddevice soundfile pyyaml

All already in requirements.txt; listed here for a fresh machine.

### 5. whisper.cpp 

Set "stt_engine": "whisper" in config.json to route transcription through whisper.cpp instead of parakeet.cpp. This was added because parakeet occasionally mishears words; whisper sometimes does better on different accents or phrasing. All other config keys remain valid, so switching back and forth is a one-line edit.

To install:

    git clone https://github.com/ggerganov/whisper.cpp
    cd whisper.cpp
    cmake -B build
    cmake --build build -j
    wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
      -O models/ggml-base.en.bin

## Installation

1. Clone or copy the project into a directory (e.g., C:/Tools/win-voice-assistant/).
2. Edit config/config.json to match your paths (parakeet binary, GGUF models, Piper binary/model, record_seconds).
3. Pre-generate voice assets (one-time, or whenever you change the fixed phrases):

       python tools/generate_voice_assets.py

   This creates assets/listening.wav and assets/exiting_assistant.wav using Piper. These are the only pre-recorded assets; all other responses are synthesized dynamically via speak_text().

4. Run:

       python main.py

   The tray icon appears. Double-tap Right Ctrl to issue a voice command.

## Configuration Reference (config/config.json)

- parakeet_exe — e.g. C:/Tools/parakeet/parakeet-cli.exe — parakeet-cli binary
- parakeet_model — e.g. .../tdt_ctc-110m-q8_0.gguf — English ASR model
- parakeet_vad_model — e.g. .../silero-vad-f16.gguf — VAD model for --vad
- piper_exe — e.g. C:/Tools/piper/piper.exe — Piper TTS binary
- piper_model — e.g. .../en_US-lessac-medium.onnx — Piper voice
- record_seconds — e.g. 5 — recording duration (set to 30/300 for longer dictation)
- speak_responses — true/false — if true, responses are spoken via Piper; if false, only notifications
- whisper_exe / whisper_model — retained for future control-word use; not currently called
- stt_engine — "parakeet" or "whisper" — selects which STT backend core/stt.py uses
- screenshot_dir — e.g. C:/Users/myuser/Pictures — directory where screenshots are saved

## Commands Reference (config/commands.yaml)

### Tier 1 (pure shell)

- open downloads / show downloads — opens shell:Downloads in Explorer
- open documents / show documents — opens shell:Personal in Explorer
- close edge / close excel / close notepad / close calculator / close explorer — terminate the process; close explorer gracefully closes file explorer windows without killing the taskbar or desktop
- Aliases quit X / exit X for close commands
- search web query — opens Edge with google.com/search?q=query
- edge, excel, notepad, calculator, github, youtube, jira, ticket-tool — opens the configured app/URL
- start work (workflow) — opens Edge, then ticket-tool, then jira
- exit / quit / shutdown assistant — speaks "Exiting assistant", then quits

### Python marker (screenshot)

- take screenshot / screenshot / capture screen — captures all monitors via PowerShell + System.Drawing, saves to ~/Pictures/Screenshot_timestamp.png, responds with the path

## Adding New Commands

The YAML is intentionally flat. To add a shell command:

    commands:
      my app: 'C:/Path/To/app.exe'
    aliases:
      open my app: my app

No Python changes needed — detect_intent matches the alias, execute runs the shell string.

To add a workflow:

    workflows:
      morning routine:
        - edge
        - my app

## Exiting the assistant

- In addition to saying "exit" / "quit" / "shutdown assistant", you can right-click the system tray icon and select Exit.

## Troubleshooting

### parakeet-cli not found or --vad unrecognized

- Confirm you downloaded v0.6.1 (or newer). The v0.6.0 release notes state "feat: standalone VAD (model head and Silero), streaming, and external VAD for transcribe", so the pre-built binary should list --vad in its help output.

- If --vad is still missing, build from source:
```bash
git clone --recursive https://github.com/mudler/parakeet.cpp
cd parakeet.cpp
cmake -B build -DPARAKEET_BUILD_CLI=ON
cmake --build build -j
```
Requires CMake (winget install Kitware.CMake), Git with submodule support, and MSVC or MinGW-w64 on PATH. No CUDA/Vulkan SDK is needed for CPU-only builds.

- Last resort: remove --vad --vad-model from core/stt.py. Transcription works for 5-second clips but will truncate on longer recordings.

### Piper produces no audio

- Verify piper_exe and piper_model paths in config.json.
- Test directly: echo "test" | C:/Tools/piper/piper.exe -m C:/Tools/piper/voices/en_US-lessac-medium.onnx -f test.wav
- Ensure sounddevice / soundfile are installed and your default audio output is set.

### Screenshot fails

- The PowerShell script uses System.Windows.Forms and System.Drawing, which are part of .NET Framework on all Windows 11 installs. If it errors, run the PowerShell snippet manually to see the exception.
- Multi-monitor setups: VirtualScreen captures all monitors. File size will be larger.

### Focus Assist toggle has no effect

- The registry value NOC_GLOBAL_SETTING_TOASTS_ENABLED lives under HKCU, no admin required.
- Some Windows 11 builds (24H2) have changed Focus Assist behavior; the registry toggle may not fully suppress notifications if Focus is managed by a different setting. This is a Windows limitation, not a script bug.

### search web opens a blank Google page

- The command only works with a query: search web quantum computing. If you say just search web, no query is appended.
- The google alias resolves to search web with no suffix. For google query support, a prefix-alias table would be needed — not implemented in this version.

## Version History

- v1.3.0 (main.py) — parakeet STT, speak_text, speak_responses flag, screenshot marker
- v1.4.0 (intent.py) — marker intent, search web prefix, removed time/mute
- v1.4.0 (actions.py) — _take_screenshot, removed time/mute/speak calls
- v1.1.0 (stt.py) — parakeet-cli with --vad
- v1.1.0 (tts.py) — speak_text via Piper + temp WAV
- v1.2.0 (commands.yaml) — Tier-1 productivity commands + screenshot marker
- v1.3.0 (generate_voice_assets.py) — reduced to listening.wav and exiting_assistant.wav only
- v1.1.0 (config.json) — added parakeet paths, speak_responses

## License

[MIT](/LICENSE)  

Note: 
- parakeet.cpp is MIT; GGUF weights derive from NVIDIA NeMo under CC-BY-4.0. 
- Piper is GPL-3.0 — check license obligations if you redistribute binaries.