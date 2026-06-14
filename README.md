# Cambridge Audio Infrared — Home Assistant Integration

A native Home Assistant integration to control Cambridge Audio devices via infrared, built on the IR platform introduced in Home Assistant 2026.4.

Supported models: **CXA60**, **CXA80** (amplifiers), **CXN100** (network player)

---

## Requirements

- Home Assistant 2026.4 or newer
- Any IR transmitter exposed to Home Assistant as an infrared emitter. An ESPHome-based IR blaster is the most common option (see [ESPHome Infrared Proxies](https://github.com/esphome/infrared-proxies)), but any integration that registers with the [infrared platform](https://www.home-assistant.io/integrations/infrared) works.

---

## Development setup

This integration is intended for inclusion in the Home Assistant core repository. To work on it locally, use the standard HA development environment.

### Running locally against Home Assistant core

1. Fork and clone [home-assistant/core](https://github.com/home-assistant/core).
2. Place the `cambridge_audio_infrared` folder under `homeassistant/components/`:

   ```
   homeassistant/components/cambridge_audio_infrared/
   ├── __init__.py
   ├── manifest.json
   ├── const.py
   ├── rc5.py
   ├── config_flow.py
   ├── media_player.py
   ├── button.py
   ├── event.py
   ├── strings.json
   └── translations/
       ├── en.json
       └── nl.json

   tests/components/cambridge_audio_infrared/
   ├── conftest.py
   ├── test_config_flow.py
   ├── test_media_player.py
   └── test_rc5.py
   ```

3. Follow the [HA development environment setup guide](https://developers.home-assistant.io/docs/development_environment) to install dependencies and run a local instance.

### Submitting to Home Assistant core

Before opening a pull request against `home-assistant/core`, make sure the integration meets the [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) requirements and passes all checks:

```bash
python -m script.hassfest          # validates manifest, strings, etc.
python -m pytest tests/components/cambridge_audio_infrared/
pre-commit run --all-files
```

See the [Contributing to Home Assistant](https://developers.home-assistant.io/docs/development_submitting) guide for the full pull request process.

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Cambridge Audio Infrared**.
3. Select your amplifier model (e.g. CXA60).
4. Select the IR emitter entity (e.g. from your ESPHome IR blaster).
5. Optionally select an IR receiver to get remote-press events (HA 2026.6+).
6. Click **Submit**.

Home Assistant will create a device with a `media_player` entity and a set of `button` entities.

> **Note:** IR is one-way, so the integration uses *assumed state*. Home Assistant tracks the last command sent but cannot verify the actual state of the amplifier.

---

## Entities

### Media Player

The `media_player` entity supports:

| Feature | Notes |
|---|---|
| Turn on / off | Sends discrete Power On / Power Off commands |
| Volume up / down | Step-based; no absolute volume level |
| Mute / unmute | Discrete Mute On / Mute Off commands |
| Source selection | See source list below |

Available sources for the CXA60:

| Source name | Input |
|---|---|
| A1 | Analogue 1 |
| A2 | Analogue 2 |
| A3 | Analogue 3 |
| A4 | Analogue 4 |
| D1 | Digital 1 |
| D2 | Digital 2 |
| D3 | Digital 3 |
| MP3 | MP3 / 3.5 mm |
| USB Audio | USB Audio |

### Buttons

A `button` entity is created for every function on the CXA60 remote:

**Power:** Power Toggle, Power On, Power Off

**Volume:** Volume Up, Volume Down, Mute Toggle, Mute On, Mute Off

**Display:** Brightness Toggle, LCD Bright, LCD Dim, LCD Off

**Speaker output:** Speaker A+B, Speaker A, Speaker B, Speaker Select

**Inputs:** Input A1–A4, Input D1–D3, Input MP3, Input USB Audio, Source Up, Source Down

**Direct mode:** Analogue Stereo Direct

**Triggers:** Trigger A, Trigger B, Trigger C

### CXN100 (network player)

The CXN100 is a network streamer, so it's exposed as a **virtual remote**: a set
of `button` entities only (no media player — IR is one-way and can't read back
transport state; for full two-way control use the official network integration).

Buttons cover transport (Play/Pause, Stop, Skip Previous/Next, Random, Repeat),
navigation (Home, Up/Down/Left/Right, Select, Return, Info, More, Digital Input
Menu), inputs (Bluetooth, USB Audio, D1, D2), Presets 1–8, power, display, and
volume/mute (the last only respond in the CXN's Digital Pre-amp mode).

> **System code:** the CXN's main commands use a base RC-5 system code that the
> device exposes as switchable between **24** and **28** (Settings menu). Pick
> the matching value during setup. Power commands use the shared CX system code
> 25 (so Power On/Off also reach a CXA amplifier on the same code), while a
> CXN-only Power Toggle avoids that.

### Remote events (optional)

If you select an IR *receiver* during setup (requires HA 2026.6+ and any IR
receiver exposed to the infrared platform, such as an ESPHome device with an IR
receiver), the integration adds an `event` entity that fires
whenever a button on the physical Cambridge Audio remote is pressed. The event
type is the command key (e.g. `volume_up`, `input_d1`), so you can trigger
automations from the real remote:

```yaml
trigger:
  - trigger: state
    entity_id: event.cambridge_audio_cxa60_remote
condition:
  - condition: template
    value_template: "{{ trigger.to_state.attributes.event_type == 'volume_up' }}"
action:
  - action: light.turn_on
    target:
      entity_id: light.listening_room
```

Each device's event entity only reacts to its own RC-5 system code(s), so the
universal **RC-CXA/C/N** remote drives the matching device: amplifier buttons
(system code 16) fire the CXA entity, network-player buttons (24/28) fire the
CXN entity. Frames for unrelated devices are ignored. One documented overlap:
the CXN's pre-amp volume/mute share system code 16 with the amplifiers, so those
presses may fire on both a CXA and a CXN event entity.

---

## Automation examples

### Turn on the amplifier and select a source

```yaml
action:
  - action: media_player.turn_on
    target:
      entity_id: media_player.cambridge_audio_cxa60
  - action: media_player.select_source
    target:
      entity_id: media_player.cambridge_audio_cxa60
    data:
      source: D1
```

### Volume up via button press

```yaml
action:
  - action: button.press
    target:
      entity_id: button.cambridge_audio_cxa60_volume_up
```

### Turn off when everyone leaves home

```yaml
trigger:
  - trigger: state
    entity_id: zone.home
    to: "0"
action:
  - action: media_player.turn_off
    target:
      entity_id: media_player.cambridge_audio_cxa60
```

---

## IR Protocol details

The CXA60 uses the **Philips RC-5** protocol:

| Parameter | Value |
|---|---|
| Protocol | RC-5 |
| System code (address) | 16 |
| Carrier frequency | 36 kHz |
| Source | [Official Cambridge Audio IR code document](https://www.cambridgeaudio.com/sites/default/files/compliance/doc/CXA%20IR%20Remote%20Control%20Codes.pdf) |

The integration uses the `RC5Command` class from the [`infrared-protocols`](https://github.com/home-assistant-libs/infrared-protocols) library (introduced in HA 2026.4). This is a hard dependency — HA 2026.4 or newer is required.

---

## Troubleshooting

**"No IR emitters found" during setup**
Make sure an IR transmitter is already added to Home Assistant via Settings → Devices & Services before setting up this integration, and that it exposes an infrared emitter entity. With ESPHome this means firmware with the IR transmitter component configured as an HA infrared proxy; other infrared-platform integrations work too.

**Commands are sent but the amplifier does not respond**
- Check that the IR blaster is physically pointed at the CXA60's IR receiver window (front panel, bottom centre).
- Verify the emitter entity is working by testing it with a different IR integration or via Developer Tools → Actions.
- Make sure nothing is blocking the line of sight between the blaster and the amplifier.

**State is wrong after power cycling**
This is expected. Because IR is one-way there is no feedback from the amplifier. You can reset the assumed state by calling `media_player.turn_on` or `media_player.turn_off` explicitly from an automation or the UI.

---

## Roadmap

- [x] CXA80 support (adds Balanced A1 and Bluetooth inputs)
- [x] IR receiver support — trigger automations from the physical remote (requires HA 2026.6+ `InfraredReceiverEntity`)
- [x] Test suite for HA integration quality scale compliance

---

## Contributing

Pull requests are welcome. When adding support for a new Cambridge Audio model:

1. Add the model's IR codes to `const.py`.
2. Add the model identifier to `SUPPORTED_MODELS`.
3. Wire up the new entities in `media_player.py` and `button.py`.
4. Update this README with the new model's source list and any protocol differences.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
