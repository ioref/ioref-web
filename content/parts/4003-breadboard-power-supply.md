---
title: Breadboard Power Supply
description: Supplies power to a breadboard, available to be used by electronic components
  plugged into it.
category: power
signal_type: n/a
image: 4003.jpg
related:
- 0502-5v-relay
- 0892-9v-battery
- 1896-servo-motor
- 4005-stepper-motor-driver
parts:
- number: '4003'
---

## About

The Breadboard Power Supply makes it easy to supply 5V and 3.3V power to components. The Breadboard Power Supply takes in 5V to 12V power via the DC barrel jack and converts it to 5V, 3.3V, and ground pins. It also provides a power switch and an LED light to show that it is powered up.

The Breadboard Power Supply is capable of supplying more power than is available on the 5V, 3.3V, and digital pins on the Arduino. So, if you need to power something like a motor it is best to use the Breadboard Power Supply. You can also use the Breadboard Power supply to power the Arduino itself.

When the Breadboard Power Supply is connected to a breadboard, it also supplies power on the read and blue power rails of the breadboard. To select if it supplies 3.3V or 5V a rail, move the small pin jumper. If the jumper bridges the 3.3V and VCC pins, then it will supply 3.3V. If it bridges the 5V and VCC pins, then it will supply 5V to that rail.

<figure class="image" style="text-align:center">   <img src="/images/parts/4003_diagram1.min.svg" alt="Breadboard Power Supply Annotated Drawing">   <figcaption style="text-align:center"><em>The Breadboard Power Supply module has multiple power output pins.</em></figcaption></figure>

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/4003_schematic1.svg" alt="Breadboard Power Supply Schematic">   <figcaption style="text-align:center"><em>The Breadboard Power Supply module supplies power to the Arduino.</em></figcaption></figure>

Here is an example showing how to power an Arduino with the Breadboard Power Supply. **When powering an Arduino this way, it is important not to connect both the Breadboard Power Supply and the Arduino's USB cable at the same time; providing power from two places can lead to big problems.**

For an example on using the Breadboard Power Supply to power both the Arduino and a [Stepper Motor](/parts/4004/), please see the [Stepper Motor Driver page](/parts/4005/).
