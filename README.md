# Windows Voice Assistant

A local, CPU-only voice assistant for Windows 11. Double-tap **Right Ctrl** to record a voice command. The assistant transcribes it with parakeet.cpp / whisper.cpp, matches the intent against a flat YAML configuration, executes the action (open apps, navigate Edge, toggle Focus Assist, take a screenshot, etc.), and provides audio/visual feedback. 

No cloud services, no GPU, no Python LLM dependency at runtime.

## Architecture Overview

Two modes of operation, selected via mode in config.json:

**Command mode** (`mode: "command"`, default):

```
Right Ctrl (double-tap)
  -> listening cue
  -> record for record_seconds
  -> transcribe (parakeet or whisper)
  -> detect_intent (commands.yaml)
  -> execute (shell / script / close / workflow / screenshot)
  -> spoken or ding feedback
  -> notification
```

**STT mode** (`mode: "stt"`):

```
Right Ctrl (double-tap) -> start streaming capture -> listening cue
Right Ctrl (double-tap) -> stop capture
  -> transcribe
  -> copy to clipboard via clip.exe
  -> positive ding + notification  (or negative ding on failure)
```

The tray icon flips between idle and listening. Exit is available from the tray context menu or (in command mode) by voice.

## Prerequisites

You need Git, downloaded binaries/models, and Python dependencies. Commands below assume Git Bash or PowerShell 7 on Windows 11.

### 1. parakeet.cpp (pre-built binary with VAD support)

Download the v0.6.1 Windows CPU x64 pre-built package, which includes the standalone Silero VAD API:

```bash 
wget https://github.com/mudler/parakeet.cpp/releases/download/v0.6.1/parakeet-v0.6.1-bin-win-cpu-x64.zip
-O parakeet-v0.6.1.zip
unzip parakeet-v0.6.1.zip -d C:/Tools/parakeet/
```
The binary is at `C:/Tools/parakeet/parakeet-cli.exe`. Verify VAD support is present:

`C:/Tools/parakeet/parakeet-cli.exe transcribe --help`

The output should list `--vad` and `--vad-model`. If those flags are missing, build from source (see Troubleshooting).

### 2. GGUF models

Download both files from the `mudler/parakeet-cpp-gguf` HuggingFace repo:

- `tdt_ctc-110m-q8_0.gguf` (177.8 MB) — English ASR, hybrid TDT+CTC, WER parity with NeMo
- `silero-vad-f16.gguf` (~1.3 MB) — Voice Activity Detection for chunking long audio

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

Unzip to `C:/Tools/piper/`. The binary is `piper.exe`.

Download the `en_US-lessac-medium` voice:

```
    mkdir -p C:/Tools/piper/voices
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
      -O C:/Tools/piper/voices/en_US-lessac-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json \
      -O C:/Tools/piper/voices/en_US-lessac-medium.onnx.json
```

Update `config.json`:

```
    "piper_exe": "C:/Tools/piper/piper.exe",
    "piper_model": "C:/Tools/piper/voices/en_US-lessac-medium.onnx"
```    

### 4. Python dependencies

```
    pip install PySide6 keyboard sounddevice soundfile numpy pyyaml
```

### 5. whisper.cpp 

Set `"stt_engine": "whisper"` in `config.json` to route transcription through whisper.cpp instead of parakeet.cpp. This was added because parakeet occasionally mishears words; whisper sometimes does better on different accents or phrasing. All other config keys remain valid, so switching back and forth is a one-line edit.

To install:

```
    git clone https://github.com/ggerganov/whisper.cpp
    cd whisper.cpp
    cmake -B build
    cmake --build build -j
    wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
      -O models/ggml-base.en.bin
```

## Installation

1. Clone or copy the project into a directory (e.g., `C:/Tools/win-voice-assistant/`).
2. Edit `config/config.json` to match your paths (parakeet, Piper, models, `screenshot_dir`).
3. Pre-generate voice assets (one-time, or whenever you change the fixed phrases):

    `python tools/generate_voice_assets.py`

This creates:

- Spoken (Piper): `listening.wav`, `command_executed.wav`, `workflow_completed.wav`, `unknown_command.wav`, `exiting_assistant.wav`, `screenshot_saved.wav`
- Synthesized: `ding.wav`, `positive_ding.wav`, `negative_ding.wav`, `close_or_exit.wav`, `camera_shutter.wav`   

4. Run:

   `python main.py`

   The tray icon appears. Double-tap Right Ctrl to issue a voice command.

## Configuration Reference (config/config.json)

| Key | Example | Description |
|---|---|---|
| `mode` | `"command"` / `"stt"` | Operating mode |
| `stt_engine` | `"parakeet"` / `"whisper"` | Speech-to-text backend |
| `whisper_exe` | `C:/Tools/whisper/whisper-cli.exe` | Whisper binary (if `stt_engine` is `whisper`) |
| `whisper_model` | `.../ggml-base.en.bin` | Whisper model |
| `parakeet_exe` | `C:/Tools/parakeet/parakeet-cli.exe` | parakeet-cli binary |
| `parakeet_model` | `.../tdt_ctc-110m-q8_0.gguf` | English ASR model |
| `parakeet_vad_model` | `.../silero-vad-f16.gguf` | Silero VAD model for `--vad` |
| `piper_exe` | `C:/Tools/piper/piper.exe` | Piper TTS binary |
| `piper_model` | `.../en_US-lessac-medium.onnx` | Piper voice |
| `record_seconds` | `5` | Fixed recording duration in command mode |
| `record_seconds_stt_max` | `120` | Safety cap in STT mode (auto-stop if second hotkey never arrives) |
| `speak_responses` | `true` / `false` | When true: spoken responses. When false: dings only |
| `screenshot_dir` | `C:/Users/myuser/Pictures` | Directory where screenshots are saved |

---

## Commands Reference (`config/commands.yaml`)

### Shell commands (`commands:`)

| Spoken phrase | Action |
|---|---|
| `edge`, `excel`, `notepad`, `calculator`, `github`, `youtube`, `jira`, `ticket-tool` | Opens the configured app/URL |
| `open downloads` / `show downloads` | Opens `shell:Downloads` in Explorer |
| `open documents` / `show documents` | Opens `shell:Personal` in Explorer |
| `search web <query>` | Opens Edge with a Google search (query is URL-encoded) |
| `take screenshot` / `screenshot` / `capture screen` | Captures all monitors, saves to `screenshot_dir` |
| `start work` (workflow) | Opens Edge -> ticket-tool -> jira |
| `exit` / `quit` / `shutdown assistant` | Exits (voice exit only in command mode) |


### Close commands (`close:`)

| Spoken phrase | Action |
|---|---|
| `close edge` / `quit edge` | Terminates `msedge.exe` |
| `close excel` / `quit excel` | Terminates `EXCEL.EXE` |
| `close notepad` / `quit notepad` | Terminates `notepad.exe` |
| `close calculator` | Terminates `calc.exe` |
| `close explorer` | Gracefully closes file explorer windows (keeps taskbar and desktop) |


### Scripts (`scripts:`)

Launch `.ps1` or `.py` scripts fire-and-forget:

```yaml
scripts:
  vpn: 'c:/users/myuser/scripts/togglevpn.ps1'
  backup: 'c:/users/myuser/scripts/backup.py'

aliases:
  toggle vpn: vpn
  start backup: backup
```

- `.ps1` -> `powershell.exe -ExecutionPolicy Bypass -NoProfile -File <script>`
- `.py` -> `sys.executable <script>` (same Python as `main.py`, so venv honoured)
- Fire-and-forget: no wait, no exit-code check
- No console window, no `cmd.exe`, no doskey interference
- If a key exists in both `commands:` and `scripts:`, `commands:` wins

### Search prefixes (`search_prefixes:`)

| Prefix | Example -> Result |
|---|---|
| `search web` | `search web elon musk` -> `q=elon%20musk` |
| `google` | `google elon musk` -> `q=elon%20musk` |
| `search` | `search quantum` -> `q=quantum` |
| `search the web` | `search the web node js` -> `q=node%20js` |

Queries are URL-encoded so multi-word phrases stay in a single tab.

---

## Modes

### Command mode (`mode: "command"`)

Double-tap Right Ctrl. Records for `record_seconds`, matches intent, executes, provides feedback. Voice "exit" / "quit" shuts down the assistant.

### STT mode (`mode: "stt"`)

Double-tap Right Ctrl to start streaming capture. Double-tap again to stop. The recorded audio is transcribed and copied to the clipboard via `clip.exe`. No intent matching, no spoken response.

- Safety cap: `record_seconds_stt_max` (default `120`) auto-stops if the second hotkey never arrives
- Microphone opening failure triggers negative ding + notification
- Clipboard write failure triggers negative ding + notification
- Empty transcription triggers negative ding + "No speech detected"

The word "exit" is transcribed and copied like any other text; the assistant does not shut down. Use the tray context menu to quit.

---

## Audio Behavior Matrix

| Event | `speak_responses: true` | `speak_responses: false` |
|---|---|---|
| Recording starts | `listening.wav` | `ding.wav` |
| Command / script launched | `command_executed.wav` | `positive_ding.wav` |
| Workflow launched | `workflow_completed.wav` | `positive_ding.wav` |
| Close app | speaks `"Closed <proc>"` via Piper | `close_or_exit.wav` |
| Screenshot | `screenshot_saved.wav` | `camera_shutter.wav` |
| Exit (voice) | `exiting_assistant.wav` | `close_or_exit.wav` |
| Unknown command | `negative_ding.wav` -> `unknown_command.wav` | `negative_ding.wav` |
| STT success | `positive_ding.wav` | `positive_ding.wav` |
| STT empty / failure | `negative_ding.wav` | `negative_ding.wav` |
| Tray Exit menu | silent | silent |

All dings and pre-recorded cues are played from disk; no runtime Piper synthesis on the feedback path. Runtime Piper synthesis (`speak_text`) is only used for dynamic responses like `"Closed msedge.exe"` and `"Process not running: notepad.exe"`.

---

## Adding New Commands

The YAML is intentionally flat. To add a shell command:

```yaml
commands:
  my app: 'C:/Path/To/app.exe'
aliases:
  open my app: my app
```

No Python changes needed.

To add a workflow:

```yaml
workflows:
  morning routine:
    - edge
    - my app
```

To add a close command:

```yaml
close:
  close spotify: 'Spotify.exe'
```

To add a script:

```yaml
scripts:
  my script: 'c:/users/myuser/scripts/my_script.ps1'
aliases:
  run my script: my script
```

---


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
- Test directly: `echo "test" | C:/Tools/piper/piper.exe -m C:/Tools/piper/voices/en_US-lessac-medium.onnx -f test.wav`
- Ensure sounddevice / soundfile are installed and your default audio output is set.

### Screenshot fails

- The PowerShell script uses System.Windows.Forms and System.Drawing, which are part of .NET Framework on all Windows 11 installs. If it errors, run the PowerShell snippet manually to see the exception.
- Multi-monitor setups: VirtualScreen captures all monitors. File size will be larger.

### search web opens a blank Google page

- The command only works with a query: search web quantum computing. If you say just search web, no query is appended.
- The google alias resolves to search web with no suffix. For google query support, a prefix-alias table would be needed — not implemented in this version.

### Cmd window / doskey output when launching apps

All `commands:` and `scripts:` entries run with `shell=False` + `CREATE_NO_WINDOW`. If you add a command needing pipes, redirection, or env expansion, you must run it through an explicit `cmd.exe /c "..."` in the YAML string — but that reintroduces doskey output. Prefer wrapping such logic in a `.ps1` or `.py` script instead.

### `stt` mode hangs or doesn't stop

- Verify the safety cap `record_seconds_stt_max` is set.
- Double-tap Right Ctrl again within the safety window to stop manually.
- Check `recordings/temp_stt.wav` is being written and overwritten between attempts.
- If `sounddevice` can't open the microphone, a negative ding plays and a "Microphone unavailable" notification appears; the tray returns to idle immediately.

### `close explorer` leaves windows open

The `Shell.Application` COM enumeration only closes windows created via the Explorer shell. Some dialogs (e.g. Control Panel windows) may not be enumerated. Taskbar and desktop always remain.

### `close X` reports "Process not running"

`taskkill` returned non-zero because the named process was not running. Harmless.

---

## Version History

| Version | Change |
|---|---|
| `main.py` v1.7.0 | Mode selection, STT streaming capture with hotkey toggle + safety cap, `speak_responses` flag, ding-vs-speak branching |
| `core/actions.py` v1.8.0 | `execute(intent, speak_responses)`, pre-recorded cues gated on the flag, dings on the false path, `screenshot_saved.wav` replaces dynamic path speech |
| `core/intent.py` v1.6.0 | Search prefixes, URL encoding, marker intents, precedence `commands:` > `scripts:` |
| `core/stt.py` v1.2.0 | Dispatcher for parakeet / whisper backends |
| `core/tts.py` v1.2.0 | `play_ding`, `speak_text` |
| `tools/generate_voice_assets.py` v1.6.0 | 6 spoken assets + 5 synthesized dings |
| `config/commands.yaml` v1.4.0 | `scripts:` section, `close:` section, `search_prefixes:` |
| `config/config.json` v1.5.0 | `mode`, `stt_engine`, `record_seconds_stt_max`, `screenshot_dir`, `speak_responses` |

---

## License

[MIT](/LICENSE)  

Note: 
- parakeet.cpp is MIT; GGUF weights derive from NVIDIA NeMo under CC-BY-4.0. 
- Piper is GPL-3.0 — check license obligations if you redistribute binaries.