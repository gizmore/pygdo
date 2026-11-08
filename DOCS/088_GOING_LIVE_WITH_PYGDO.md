# Going Live with PyGDO

This is an operator's overview of the current Mira, Audio, Video and Translate
modules. Commands require the relevant modules, permissions and a running Dog;
the trigger prefix depends on the channel. Examples below use `$`.

## Live-show mode

- `$live` reports the effective mode; `$live off`, `$live work`, `$live show`
  and `$live discuss` request a mode. `$video.liveshow` is the full method name;
  the legacy forms `$live 0` and `$live 1` mean `off` and `show`.
- The setting is `mira_livemode`. Until it is explicitly saved, an existing
  `mira_quacking` value is read as `show` when on and `off` when off.
  Routed chat and microphone events carry the mode as `--live=<mode>`.
- Selecting `show` requests the 3D duck and microphone meter; the other modes
  request hiding them. Only `show` enables automatic live join greetings.
  No mode starts a broadcast or microphone capture. `work` and `discuss` are
  distinct labels; they do not yet control music or route call audio.

## Audio and microphone

- `$mic --lang=de 1` requests continuous microphone transcription in German;
  `$mic 0` disables it without clearing the saved language. The microphone
  operator and audio session must be configured. People near the input may be
  transcribed.
- `$audio.language de` sets the module-wide transcription language. Recognition
  quality and available languages depend on the transcription setup.
- `$audio.meter 1` / `$audio.meter 0` start or stop level monitoring.
  `$video.mic 1` / `$video.mic 0` show or hide the video meter separately;
  showing it does not start capture. Its recognized-text display may be visible
  to viewers. An OFF indicator describes Dog's monitoring, not hardware mute
  or another application's microphone.
- `$spk --lang=de Hallo zusammen` queues spoken text. `$audio.stop` requests
  cancellation of Dog-managed speech and supported audio playback, not unrelated
  desktop audio or microphone capture.
- Audio module configuration includes `audio_output_device`,
  `audio_output_session_user`, `audio_operator`, `audio_microphone`,
  `audio_microphone_session_user`, `audio_microphone_language` and
  `audio_transcript_min_letters`. `audio_tts_backend` selects `espeak` or `piper`;
  Piper's binary and language-specific voice-model paths are configured
  separately. Voice availability depends on the installed backend and models.

## Translation

Translation is opted in per channel. `$trans` shows the channel state and target
languages. `$trans --lang=de 1` adds German; `$trans --lang=de 0` removes it.
`$trans --pause=1` pauses automatic translation while retaining the targets;
`$trans --pause=0` resumes it. Pausing also disables `$all` speech translation,
but not explicit one-off translations. The provider must be configured; see the
[Translate README](../gdo/translate/README.md). Channel translation is separate
from microphone transcription and does not provide speaker identification.

## Video and avatar

`$video.start`, `$video.stop` and `$video.status` control and inspect the video
connector. Set `video_mode` before starting it:

- `off`: no video capture or output.
- `screensharing`: a transparent desktop overlay for a separately shared X11
  desktop. It does not itself start sharing in Discord or another application.
- `virtualwebcam`: compose configured sources into a preview and/or a virtual
  camera. `video_output_preview`, `video_live` and `video_output_device` select
  the outputs; preview size uses `video_preview_w` and `video_preview_h`.

Example for a desktop overlay, after checking the intended destination:

```text
$conf video video_mode screensharing
$video.start
$video.status
```

Use `$video.preview` for the running virtual-webcam compositor's preview.
Other video configuration fields select desktop, background, overlay, file and
webcam sources. Requirements and details are in the
[Video README](../gdo/video/README.md).

- `$video.duck 1` / `0` show or hide the 2D duck and its speech captions.
- `$video.duck3d 1` / `0` request the experimental 3D duck or its removal.
  It needs the optional renderer dependencies and a working display.
- `$duck.anim` lists animations; `$duck.anim work` selects one. Optional text
  can be spoken, and `--base=1` or `--base=0` selects persistent or temporary
  behavior. `$video.ducktext <text>` shows a short caption without speech.
- `$duck.welcome <nickname>` requests a greeting. Automatic join greetings
  require the live flag and channel opt-in via
  `$confc video.welcome video_welcome_enabled 1`; use `0` to disable them.
  They can reveal participants' nicknames to the audience.

## Show effects

- `$video.media <url>` displays an image or silent video; `--width`, `--height`,
  `--x` and `--y` set its box. `$video.media off` removes it.
- `$video.vintage 1` / `0` enables or disables flicker and scratches. Flicker
  can affect viewers sensitive to flashing.
- `$video.magnify 1` / `0` toggles the mouse lens in virtual-webcam mode.
- `$video.layer` controls supported layers; `$video.draw <prompt>` requests a
  drawing. `$video.close <key>` removes an effect and `$video.close --all`
  removes the effects without stopping the worker.

## Before and during a show

Check microphone and output routing, participant consent, the actual shared
source and what captions or names viewers can see. Avoid feeding Mira's output
back into the microphone. Use a separate Test Dog when testing changes.
Commands that say they are queued acknowledge a request, not successful
capture, audible speech, a visible overlay or a live broadcast. Confirm the
result in the target application. Some controls are owner-only or channel-staff
only; a live flag alone is not a complete show setup.

For operational details, see the [Audio README](../gdo/audio/README.md),
[Video README](../gdo/video/README.md) and
[Translate README](../gdo/translate/README.md).
