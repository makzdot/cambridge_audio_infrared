---
title: Cambridge Audio Infrared
description: Integration to control Cambridge Audio amplifiers and network players using an infrared transmitter.
ha_category:
  - Media player
ha_release: 2026.7
ha_iot_class: Assumed State
ha_codeowners:
  - '@makzdot'
ha_domain: cambridge_audio_infrared
ha_config_flow: true
ha_platforms:
  - button
  - event
  - media_player
ha_integration_type: device
ha_quality_scale: bronze
---

The **Cambridge Audio Infrared** {% term integration %} lets you control Cambridge Audio amplifiers and network players using any infrared transmitter previously configured in Home Assistant.

Because the integration communicates over infrared, it operates in a one-way, fire-and-forget fashion: commands are sent to the device but there is no feedback channel to confirm its current state. The integration therefore uses assumed states.

## Prerequisites

Before setting up the Cambridge Audio Infrared integration, you need a working infrared transmitter set up in Home Assistant that exposes an [Infrared](/integrations/infrared/) entity. For example, you can use an ESPHome device with an IR LED pointed at your Cambridge Audio unit.

Optionally, you can also configure an infrared **receiver**. When set, the integration adds an event entity that fires whenever a button on the physical Cambridge Audio remote is pressed, so you can trigger automations from the original remote.

{% include integrations/config_flow.md %}

{% configuration_basic %}
Model:
  description: The Cambridge Audio model to control (CXA60, CXA80, or CXN100).
Infrared transmitter:
  description: The infrared emitter entity used to send commands. This must be an entity provided by a hardware integration (such as ESPHome) that has already been set up with an IR transmitter.
Infrared receiver:
  description: Optional. An infrared receiver entity. When provided, an event entity is added that fires on presses of the physical Cambridge Audio remote.
System code:
  description: CXN100 only. The RC-5 system code the CXN is set to (24 or 28, configurable in the device's settings menu).
{% endconfiguration_basic %}

## Supported devices

The following devices are supported:

- **CXA60** and **CXA80** integrated amplifiers
- **CXN100** network player

## Supported functionality

The **Cambridge Audio Infrared** integration provides the following entities.

### Media player

The CXA60 and CXA80 amplifiers are exposed as a media player entity.

- **Supported features**: Turn on, turn off, volume up, volume down, mute, and source selection.

The CXN100 is a network player and is not exposed as a media player; it is provided as buttons only (see below). For full, two-way control of a CXN100, use the [Cambridge Audio](/integrations/cambridge_audio/) integration over the network instead.

### Buttons

A button entity is created for each function on the device's remote.

- **Amplifiers (CXA60/CXA80)**: power, volume and mute, display brightness, speaker output (A/B/A+B), source inputs, analogue stereo direct mode, and the 12&nbsp;V trigger outputs. The CXA80 adds Balanced A1 and Bluetooth inputs.
- **Network player (CXN100)**: a virtual remote with transport controls (play/pause, stop, skip, random, repeat), navigation (home, arrows, select, return, info, menu), inputs (Bluetooth, USB audio, D1, D2), presets 1&ndash;8, power, and display controls.

### Events

If an infrared receiver was configured, a **Remote** event entity is added. It fires whenever a recognized button on the physical Cambridge Audio remote is received, with the button name as the event type. The universal RC-CXA/C/N remote sends each device's commands on a different RC-5 system code, so each device's event entity reacts only to its own buttons.

## Known limitations

- The integration uses assumed state, meaning Home Assistant cannot read the actual state of the device (for example, whether it is on or off, the current volume, or the selected source).
- Volume control is step-based only; there is no way to set an absolute volume level.
- The CXN100 is exposed as buttons only, because infrared is one-way and cannot read back the player's transport or now-playing state.

## Removing the integration

This integration follows standard integration removal.

{% include integrations/remove_device_service.md %}
