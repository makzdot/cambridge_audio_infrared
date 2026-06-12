# Cambridge Audio Infrared — Home Assistant Integration

A custom Home Assistant integration to control Cambridge Audio amplifiers via infrared, built on the native IR platform introduced in Home Assistant 2026.4.

Supported models: **CXA60** (CXA80 support planned)

---

## Requirements

- Home Assistant 2026.4 or newer
- An ESPHome-based IR blaster already set up as an infrared emitter in Home Assistant (see [ESPHome Infrared Proxies](https://github.com/esphome/infrared-proxies))

---

## Installation

### Manual

1. Download or clone this repository.
2. Copy the `cambridge_audio_infrared` folder into your Home Assistant `config/custom_components/` directory:

   ```
   config/
   └── custom_components/
       └── cambridge_audio_infrared/
           ├── __init__.py
           ├── manifest.json
           ├── const.py
           ├── rc5.py
           ├── config_flow.py
           ├── media_player.py
           ├── button.py
           ├── strings.json
           └── translations/
               ├── en.json
               └── nl.json
   ```

3. Restart Home Assistant.

### HACS (manual repository)

1. In HACS, go to **Integrations → Custom repositories**.
2. Add the URL of this repository and set the category to **Integration**.
3. Install it and restart Home Assistant.

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Cambridge Audio Infrared**.
3. Select your amplifier model (e.g. CXA60).
4. Select the IR emitter entity from your ESPHome IR blaster.
5. Click **Submit**.

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

The integration uses the `RC5Command` class from the [`infrared-protocols`](https://github.com/home-assistant-libs/infrared-protocols) library when available, and falls back to a pure-Python RC-5 encoder that produces equivalent raw timings if the class is not yet present in your HA version.

---

## Troubleshooting

**"No IR emitters found" during setup**
Make sure your ESPHome IR blaster is already added to Home Assistant via Settings → Devices & Services before setting up this integration. The ESPHome device must expose an infrared emitter entity (requires ESPHome firmware with the IR transmitter component configured as an HA infrared proxy).

**Commands are sent but the amplifier does not respond**
- Check that the IR blaster is physically pointed at the CXA60's IR receiver window (front panel, bottom centre).
- Verify the emitter entity is working by testing it with a different IR integration or via Developer Tools → Actions.
- Make sure nothing is blocking the line of sight between the blaster and the amplifier.

**State is wrong after power cycling**
This is expected. Because IR is one-way there is no feedback from the amplifier. You can reset the assumed state by calling `media_player.turn_on` or `media_player.turn_off` explicitly from an automation or the UI.

---

## Roadmap

- [ ] CXA80 support (adds Balanced A1 and Bluetooth inputs)
- [ ] IR receiver support — trigger automations from the physical remote (requires HA 2026.6+ `InfraredReceiverEntity`)
- [ ] HACS default repository listing

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
