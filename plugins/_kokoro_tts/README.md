# Kokoro TTS

Built-in speech synthesis plugin backed by Kokoro.

## Behavior

- Registers Kokoro as the active TTS provider when the plugin is enabled.
- Keeps browser-native `speechSynthesis` as the fallback path when disabled.
- Expects the optional voice extra to be installed before the plugin is enabled.

## Config

- `voice`: Kokoro voice identifier
- `speed`: Kokoro playback speed multiplier

## Routes

- `POST /api/plugins/_kokoro_tts/synthesize`
- `POST /api/plugins/_kokoro_tts/status`

## Optional Dependency

Install `pip install -r requirements.voice.txt` before enabling `_kokoro_tts`.
