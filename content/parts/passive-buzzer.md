---
title: Passive Buzzer
description: Makes variable-pitch beeping, driven by the frequency of a changing (alternating
  current) power source connected to it.
category: output
subcategory: sound
signal_type: n/a
image: passivebutt.jpg
inventory_group: buzzers
related:
- pancake-vibration-motor
- active-buzzer
parts:
- number: 0496
---

## About

A passive buzzer requires an AC (alternating current) power source to make noise, and will not make sounds if connected to a DC voltage. This is because it needs the frequency of the power source, which oscillates back and forth, to drive the frequency of the buzzer. However, this also affords the passive buzzer more variability than the active buzzer.

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/passive buzzer.drawio.svg" alt="Passive buzzer schematic for code below"> <figcaption style="text-align:center"><em>Passive buzzer schematic for code below</em></figcaption></figure>

```
const int BUZZERPIN = 8;

void setup() {
  pinMODE(BUZZERPIN, OUTPUT);
}

void loop() {
    tone(BUZZERPIN, 500);
    delay(200);
    tone(BUZZERPIN, 1000);
    delay(200);
}
```
