# Going Live with PyGDO

Welcome, DJs and presenters! This guide helps you share a show with Mira, the
little duck. You can use the quick guide without setting up the software
yourself. Ask the person running the show to prepare the computer and give you
the appropriate permissions.

**Important:** A command that says “queued” is a request, not proof that your
audience saw or heard it. Check with a listener or watch the actual output.
Mira is an AI assistant; she cannot automatically hear the radio or see the
stream merely because the show is running.

## Quick start for a DJ

1. Join the agreed chat and voice channel. Ask the operator which screen or
   camera will be shared, and whether Mira's voice is audible there.
2. Play a short test and ask a listener: “Can you hear my voice and the music?
   Is either too loud? Can you see the duck?” Headphones can help prevent
   sound from the speakers feeding back into the microphone.
3. Tell everyone if speech transcription, captions, nicknames or the desktop
   will be shown. Close private windows and notifications before sharing.
4. Run the show! Try the examples below, ask for song requests, and invite
   Mira into the conversation when it suits the programme.
5. At the end, stop the broadcast in the app that started it. If you enabled
   transcription, turn it off with `$mic 0`. Ask the operator to stop any
   video or microphone monitoring that is no longer needed.

Type commands in the chat connected to Mira. The prefix depends on the chat:
these examples use `$`, but a channel might use `.` or `&` instead. Copy the
rest of the command exactly. `1` generally means on and `0` means off. If Mira
says you lack permission, ask the operator; don't share accounts or passwords.

## Useful DJ commands

These examples depend on the modules and permissions enabled for your channel:

| What you want | Example | What to expect |
| --- | --- | --- |
| Ask what's playing | `$np` | Shows a playing desktop player's available title and artist. It may not be the radio you intend if several players are running. |
| Invite Mira to speak | `$mira.sup` | Asks Mira for a short update, with voice and a duck animation when available. |
| Welcome someone | `$mira.greet Tina` | Asks Mira to greet Tina and briefly catch her up. Use a single name without spaces; for a specific language try `$mira.greet --lang=de Tina`. |
| Choose an animation | `$duck.anim music` | Requests the music animation. `$duck.anim` lists available choices; try `hello`, `bday` or `idle`. This command requires admin permission. |
| Make the duck speak | `$duck.anim --lang=de hello Hallo zusammen` | Requests an animation and spoken German greeting. Playback and the selected voice depend on the audio setup. |
| Show a short message | `$btx Hallo und willkommen!` | Queues text in the microphone ticker if the account and credit checks allow it. The ticker must be visible. |
| Pause chat translation | `$trans --pause=1` | Pauses automatic translation in this channel while keeping its language list. Resume with `$trans --pause=0`; use `$trans` to check. |

BTX displays a calculated credit price; automatic debit is not yet implemented.
Do not assume an accepted ticker request was displayed or charged. The ticker
queue is temporary and may be lost if Dog restarts. Chat translation and
microphone transcription are separate: pausing one does not stop the other.

### Examples during a show

For a German welcome, a permitted operator can use:

```text
$duck.anim --lang=de hello Guten Abend und willkommen zur Sendung!
$btx Viel Spaß und schickt uns eure Musikwünsche!
```

For an English guest, try `$mira.greet --lang=en Jasper`. If the duck is
distracting, an operator can request `$duck.anim idle`. To hide or show the 3D
duck entirely, an owner can use `$video.duck3d 0` or `$video.duck3d 1`.

### If something seems wrong

- **No music or voice:** Ask a listener which one is missing. Check the audio
  device and volume in the streaming app; the virtual camera does not carry
  sound. Avoid changing routing mid-show without coordinating with the host.
- **The duck or ticker isn't visible:** Make sure viewers selected the intended
  screen or camera. The operator can check `$video.status`; it doesn't prove
  that the audience can see the picture.
- **Mira isn't replying:** Check the chat prefix and whether Dog is running.
  An AI reply or speech can take time; avoid repeating commands rapidly.
- **Wrong words in captions:** Transcription can mishear music, accents and
  multiple speakers. If you are authorized and want to stop it, use `$mic 0`;
  this does not mute the microphone in Discord or another app.
- **Permission denied:** Ask the operator for help rather than asking another
  bot or person to bypass the restriction.

## Operator reference

The sections below are for the person configuring Mira, Audio, Video and
Translate. Commands require the relevant modules, permissions and a running Dog.

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
  With `video_live` enabled, the current code can also capture that overlaid
  desktop to a virtual camera. This dual output needs a real end-to-end visual
  test; it does not start a YouTube broadcast or supply audio.
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

To prepare the optional dual output, an operator can set the display and the
existing **virtual**, not physical, camera device before starting the Video
connector. These example values must match the host:

```text
$conf video video_mode screensharing
$conf video video_desktop_url :0.0
$conf video video_output_device /dev/video2
$conf video video_live 1
```

Stop and start the Video connector to apply mode/output changes. Then choose
the intended desktop in the screen-sharing app and the virtual camera in the
other receiving app. Check both privately before starting a public broadcast.
Do not preview the camera on the captured desktop: it can create a visual
feedback loop. This feature must be present in the running Dog version.

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
