---
name: voiceover
description: Adding AI-generated voiceover to Remotion compositions using TTS
metadata:
  tags: voiceover, audio, tts, speech, calculateMetadata, dynamic duration, elevenlabs, tencentcloud
---

# Adding AI voiceover to a Remotion composition

Use a TTS provider to generate speech audio per scene, then use [`calculateMetadata`](./calculate-metadata) to dynamically size the composition to match the audio.

## Choosing a TTS provider

### Provider comparison

| Provider | Cost | Chinese quality | Notes |
|----------|------|----------------|-------|
| **ElevenLabs** | Free tier limited; paid for library voices | Good (paid), weak (free tier) | Best for English; free tier has restricted voice access |
| **Tencent Cloud TTS** | ~1 million chars/month free | Excellent (native Chinese) | Best for Chinese content; standard API via SDK |
| **Open-source (ChatTTS/CosyVoice/GPT-SoVITS)** | Free (local) | Excellent | Requires GPU; see [Open-source local TTS](#open-source local-tts) |

**Recommendation:**
- Chinese content → Tencent Cloud TTS (free, natural pronunciation, no GPU needed)
- English content → ElevenLabs (best voice variety)
- Privacy/no GPU → MeloTTS (lightweight, CPU-only)
- Best quality + GPU available → CosyVoice 2 or ChatTTS

If the user has not specified a TTS provider, ask which language the content is in and recommend accordingly.

## Generating audio with Tencent Cloud TTS (recommended for Chinese)

### Prerequisites

1. Tencent Cloud account with TTS service enabled (https://console.cloud.tencent.com/tts)
2. API keys: `SecretId` and `SecretKey` from https://console.cloud.tencent.com/cam/capi. Store these in your `.env` file as shown in the Configuration section below.
3. Install SDK: `npm install tencentcloud-sdk-nodejs`

### Configuration

```bash title=".env"
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key
# Optional: voice type, speed, volume
# VOICE_TYPE=101001  # default: 智瑜 (female, professional)
# TTS_SPEED=0        # 0=normal, range 0-2
# TTS_VOLUME=0       # 0=normal, range 0-10
```

### Popular voice types

| VoiceType | Name | Description |
|-----------|------|-------------|
| 101001 | 智瑜 | Female, professional (recommended) |
| 101002 | 智聆 | Female, standard |
| 101004 | 智美 | Female, gentle |
| 101005 | 智云 | Male, mature |
| 101016 | 智莉 | Female, sweet |

### Core API call

```ts title="generate-voiceover.ts"
import tencentcloud from "tencentcloud-sdk-nodejs";

const TtsClient = tencentcloud.tts.v20190823.Client;

const client = new TtsClient({
  credential: { secretId: process.env.TENCENT_SECRET_ID, secretKey: process.env.TENCENT_SECRET_KEY },
  region: "ap-guangzhou",
  profile: { httpProfile: { endpoint: "tts.tencentcloudapi.com" } },
});

const response = await client.TextToVoice({
  Text: "欢迎使用语音合成服务。",
  SessionId: `scene-${Date.now()}`,
  VoiceType: parseInt(process.env.VOICE_TYPE ?? "101001", 10),
  Speed: parseFloat(process.env.TTS_SPEED ?? "0"),
  Volume: parseFloat(process.env.TTS_VOLUME ?? "0"),
  Codec: "mp3",
  SampleRate: 16000,
});

const audioBuffer = Buffer.from(response.Audio, "base64");
writeFileSync(`public/audio/${chapterId}/${scene.id}.mp3`, audioBuffer);
```

## Generating audio with ElevenLabs (recommended for English)

### Prerequisites

1. ElevenLabs account (https://elevenlabs.io)
2. API key from https://elevenlabs.io/app/settings/api-keys
3. Free tier limitations: library voices require paid plan; use `eleven_turbo_v2_5` model with built-in voices

### Configuration

```bash title=".env"
ELEVENLABS_API_KEY=your_api_key
# Optional: voice ID (default: built-in voice for free tier)
# VOICE_ID=pNInz6obpgDQGcFmaJgB  # Adam (free tier)
```

### Core API call

```ts title="generate-voiceover.ts"
const response = await fetch(
  `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
  {
    method: "POST",
    headers: {
      "xi-api-key": process.env.ELEVENLABS_API_KEY!,
      "Content-Type": "application/json",
      Accept: "audio/mpeg",
    },
    body: JSON.stringify({
      text: "Welcome to the show.",
      model_id: "eleven_turbo_v2_5",  // free tier compatible
      voice_settings: { stability: 0.5, similarity_boost: 0.75 },
    }),
  },
);

const audioBuffer = Buffer.from(await response.arrayBuffer());
writeFileSync(`public/audio/${chapterId}/${scene.id}.mp3`, audioBuffer);
```

## Open-source local TTS

For scenarios requiring offline execution, privacy, or unlimited free usage.

### MeloTTS (CPU-compatible, lightweight)

```bash
pip install melotts
```

```python
from melotts import MeloTTS
tts = MeloTTS(language="ZH")
tts.tts_to_file("你好世界", "output.wav")
```

- No GPU required, runs on CPU
- Lower quality compared to cloud APIs
- Apache 2.0 license

### CosyVoice 2 (GPU required, best quality)

GitHub: https://github.com/FunAudioLLM/CosyVoice

- Top-tier Chinese TTS quality
- 3-second zero-shot voice cloning
- Requires high-end GPU (e.g., A100 or RTX 4090)
- Apache 2.0 license

### ChatTTS (GPU required, best for conversational)

GitHub: https://github.com/2noise/ChatTTS

- Best for dialogue/conversational content
- Supports laughter, pauses, natural speech features
- MIT license

### GPT-SoVITS (GPU recommended, best for cloning)

GitHub: https://github.com/RVC-Boss/GPT-SoVITS

- Few-shot voice cloning (minutes of audio)
- Can run on GTX 1660
- Largest community, most tutorials
- MIT license

## Dynamic composition duration with calculateMetadata

Use [`calculateMetadata`](./calculate-metadata.md) to measure the [audio durations](./get-audio-duration.md) and set the composition length accordingly.

```tsx
import { CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDuration } from "./get-audio-duration";

const FPS = 30;

const SCENE_AUDIO_FILES = [
  "voiceover/my-comp/scene-01-intro.mp3",
  "voiceover/my-comp/scene-02-main.mp3",
  "voiceover/my-comp/scene-03-outro.mp3",
];

export const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const durations = await Promise.all(
    SCENE_AUDIO_FILES.map((file) => getAudioDuration(staticFile(file))),
  );

  const sceneDurations = durations.map((durationInSeconds) => {
    return durationInSeconds * FPS;
  });

  return {
    durationInFrames: Math.ceil(sceneDurations.reduce((sum, d) => sum + d, 0)),
  };
};
```

The computed `sceneDurations` are passed into the component via a `voiceover` prop so the component knows how long each scene should be.

If the composition uses [`<TransitionSeries>`](./transitions.md), subtract the overlap from total duration: [./transitions.md#calculating-total-composition-duration](./transitions.md#calculating-total-composition-duration)

## Rendering audio in the component

See [audio.md](./audio.md) for more information on how to render audio in the component.

## Delaying audio start

See [audio.md#delaying](./audio.md#delaying) for more information on how to delay the audio start.
