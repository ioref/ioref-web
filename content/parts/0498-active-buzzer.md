---
title: Active Buzzer
description: Makes a high-pitched beeping sound when powered with a steady (direct current)
  power source.
category: output
subcategory: sound
signal_type: n/a
image: 0496.jpg
inventory_group: sound
related:
- 0450-pancake-vibration-motor
- 0496-passive-buzzer
parts:
- number: 0498
---

## About

Active buzzers have a built-in frequency and loudness, and thus are simple to wire: they only need power and ground. You should power them with DC (not AC, as they need a constant current to produce sound). These are mainly useful for signaling or an alarm.

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/active buzzer.drawio.svg" alt="Active buzzer schematic for code below"> <figcaption style="text-align:center"><em>Active buzzer schematic for code below</em></figcaption></figure>

```
const int buzzerPin = 8;

void setup() {
  pinMode(buzzerPin, OUTPUT); // initialize digital pin 8 as an output
}

void loop() {
  digitalWrite(buzzerPin, HIGH); // turn the buzzer on (HIGH is the voltage level)
  delay(1000); // wait for a second
  digitalWrite(buzzerPin, LOW); // turn the buzzer off by making the voltage LOW
  delay(1000); // wait for a second
}
```

## Resources

- https://www.instructables.com/ACTIVE-BUZZER-WITH-ARDUINO-UNO-R3/
