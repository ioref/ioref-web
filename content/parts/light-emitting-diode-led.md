---
title: Light Emitting Diode (LED)
description: Illuminates when power flows through. It is a diode, so only allows power to
  flow in one direction.
category: output
subcategory: light
signal_type: n/a
image: 0894.jpg
related:
- photoresistor
- infrared-remote
parts:
- number: 0894
---

## About

LEDs are a commonly used component, as the most straightforward way to generate light, requiring only power and ground. The most basic LEDs have two electrical leads coming out of the casing. The longer lead (the anode) is positive and must be connected to power, while the shorter lead (the cathode) is negative and must be connected to ground. If the leads are swapped, power will not flow through and illuminate the LED, as LEDs are diodes, only allowing power to flow in one direction.

There are also more complex LEDs with three leads corresponding to red, green, and blue, and a fourth lead to power or ground depending on the type. These can be supplied in various configurations to light up the LED with the whole spectrum of color.

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/led.drawio.svg" alt="LED Schematic"> <figcaption style="text-align:center"><em>LED Schematic </em></figcaption></figure>

```
// alternating flashing LED_A and LED_B

const int LED_A = 9;
const int LED_B = 5;

void setup() {
  pinMode(LED_A, OUTPUT);
  pinMode(LED_B, OUTPUT);
}

void loop() {
  digitalWrite(LED_A, HIGH);
  digitalWrite(LED_B, LOW);
  delay(1000);
  digitalWrite(LED_B, HIGH);
  digitalWrite(LED_A, LOW);
  delay(1000);
}
```
