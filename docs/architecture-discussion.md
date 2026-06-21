# New integration proposal: Cambridge Audio Infrared (`cambridge_audio_infrared`)

## Summary

I'd like to propose a new integration, **Cambridge Audio Infrared**, that controls
Cambridge Audio audio gear over infrared using the first-party
[`infrared`](https://www.home-assistant.io/integrations/infrared/) platform. It
covers devices that have **no network interface at all** (the CXA60/CXA80
integrated amplifiers, and the same RC-5 family used by the CXC CD transport) as
well as the CXN100 network player, which also accepts IR.

Before opening a code PR I'd like to align on one point: how this should relate
to the existing **`cambridge_audio`** (StreamMagic) integration, since they share
a manufacturer/brand.

## Motivation

Today there is no way to bring a Cambridge Audio CXA60/CXA80 amplifier into Home
Assistant. These are popular integrated amplifiers with **no network
connectivity** — their only remote-control interface is infrared (RC-5). With the
`infrared` platform now in core, an IR-based integration is the natural and only
way to support them.

The integration also supports the CXN100 network player as a virtual remote
(buttons), for users who prefer/needs IR control or want a unified remote setup.

## Why a separate integration (and not part of `cambridge_audio`)

The existing `cambridge_audio` integration targets **StreamMagic network
players** over the local network: two-way, with full state feedback. That is a
fundamentally different transport and device class from what this proposal
covers:

| | `cambridge_audio` (existing) | `cambridge_audio_infrared` (proposed) |
|---|---|---|
| Transport | Network (StreamMagic API) | Infrared (RC-5) |
| Direction | Two-way, real state | One-way, assumed state |
| Devices | Networked streamers (CXN…) | CXA60/CXA80 amps, CXC, CXN100 |
| Dependency | StreamMagic library | `infrared` platform |

Crucially, the CXA amplifiers (and CXC transport) **cannot** be served by the
existing integration at all — they have no network stack. Folding IR control into
the network integration would mean mixing two unrelated transports and a
two-way device model with a one-way assumed-state one.

There is direct precedent for this split: **`samsung_infrared`** exists as a
separate IR integration alongside the network-based `samsungtv` integration, also
built on the `infrared` platform. This proposal follows the same pattern and the
same `<brand>_infrared` naming.

## Proposed design

- Built on the `infrared` platform: entities subclass
  `InfraredEmitterConsumerEntity` and send RC-5 commands via the configured IR
  emitter; availability tracks the underlying emitter.
- **Assumed state** (IoT class `assumed_state`), as IR is fire-and-forget.
- Config flow: pick the model and the IR emitter; optionally an IR **receiver**
  (when set, an `event` entity fires on presses of the physical remote). The
  CXN100's switchable RC-5 system code (24/28) is selected during setup; a
  reconfigure flow allows changing these later.
- Platforms: `media_player` (amplifiers), `button` (a per-function virtual
  remote for all models), and `event` (optional, remote-press feedback via an IR
  receiver).
- Targets the Bronze quality scale (config-flow tests, runtime data, shared base
  entity, entity/icon translations, diagnostics, strict typing).

## Supported devices

- **CXA60 / CXA80** integrated amplifiers — media player + buttons.
- **CXN100** network player — buttons (virtual remote). For full two-way control
  of a CXN100, the existing `cambridge_audio` integration remains the right
  choice; this integration is complementary.

RC-5 codes are taken from Cambridge Audio's official IR code documents and
verified on real hardware.

## Open questions for the team

1. **Naming / overlap:** is a separate `cambridge_audio_infrared` domain the
   right call (consistent with `samsung_infrared`), or is there a preference for
   grouping under the existing Cambridge Audio brand in some way?
2. **Brand assets:** should the brands entry live under its own
   `core_integrations/cambridge_audio_infrared/`, or be grouped with the existing
   `cambridge_audio` brand?
3. **IR codes:** the RC-5 code tables currently live in the integration. Would
   you prefer them contributed upstream to the `infrared-protocols` library
   (as `samsung_infrared` does with its Samsung codes)?

Happy to adjust scope or approach based on feedback before submitting the PR.
