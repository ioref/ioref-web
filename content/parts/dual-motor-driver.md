---
title: dual motor driver
description: Able to drive two motors both clockwise and counterclockwise
category: output
subcategory: movement
signal_type: Continuous
image: dualmotor.jpg
related:
- h-bridge-motor-driver
parts:
- number: 0482
---

## About

The DRV8833 dual motor driver can be used for bidirectional control of two brushed DC motors at 2.7 V to 10.8 V.

## Resources

<figure class="image" style="text-align:center"> <img src="/images/parts/dualdiagram.png" alt="Pinout for dual motor driver"> <figcaption style="text-align:center"><em>Pinout for dual motor driver | Image from <a href="https://www.pololu.com/product/2130">pololu </a> </em></figcaption></figure>

Note that "GPIO" above means "general purpose input/output" and corresponds to digital pins on the Arduino.

All GND pins must be connected to ground, and VIN (powering the motors) takes 2.7V to 10.8V. The leads of the DC motors must be connected to their output pins (motor A has both leads to motor A output pins, and the same applies to motor B). All 4 signal pins (BIN1, BIN2, AIN2, AIN1) must be connected to digital pins on the Arduino. These are a bit trickier, but they dictate the polarity of voltage and therefore the direction of rotation. The xIN1 and xIN2 pins must be a HIGH/LOW pair for the motor to spin—supplying HIGH to both or LOW to both won't make the motor spin; but having xIN1 be HIGH and xIN2 be LOW will make the motor spin in the opposite direction than if xIN2 was HIGH and xIN1 was LOW.
