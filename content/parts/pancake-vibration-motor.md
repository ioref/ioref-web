---
title: Pancake Vibration Motor
description: Vibrates quickly when powered. Usually used as a simple tactile signal. Operates
  at 5V.
category: output
subcategory: movement
signal_type: n/a
image: 0450.jpg
related:
- active-buzzer
- passive-buzzer
- dc-motor
- transistor-pn2222
parts:
- number: '0450'
---

## About

Vibration motors are perfect as non-audible indicators. Use in any number of applications to indicate to the wearer when a status has changed. The unit vibrates softly but noticeably. (Adapted from Sparkfun)

There are two primary types:

<figure class="image" style="text-align:center"> <img src="/images/parts/era motor.jpg" alt="ERA vibration motor"> <figcaption style="text-align:center"><em>ERA vibration motor | Image from <a href="https://www.precisionmicrodrives.com/eccentric-rotating-mass-vibration-motors-erms">precisionmicrodrives.com</a> </em></figcaption></figure>

**Eccentric Rotating Mass** vibration motors use the magnetic field from an electrical current to drive an object in a circle. The rotating mass is off-center from the point of rotation, which produces an uneven centripetal force, causing vibrations. The DC current supplied dictates the vibrational intensity. (Adapted from [Azom.com](https://www.azom.com/article.aspx?ArticleID=15670))

<figure class="image" style="text-align:center"> <img src="/images/parts/lra motor.jpg" alt="LRA vibration motor"> <figcaption style="text-align:center"><em>LRA vibration motor | Image from <a href="https://www.precisionmicrodrives.com/linear-resonant-actuators-lras">precisionmicrodrives.com</a> </em></figcaption></figure>

A **Linear Resonant Actuator** uses an alternative current (AC) voltage to drive a voice coil. This voice coil is pressed against a moving mass which is attached to a spring. When the voice coil is at the same resonant frequency as the spring, a magnetic field is generated and the whole actuator vibrates with a noticeable force.

Both the frequency and the amplitude of the actuator can be adjusted by changing the AC input. However, regardless of the input, the actuator must be driven at its resonant frequency to generate a large enough force. As such, linear resonant actuators can only be effectively used in a narrow frequency range; and they are ideal for those who wish to operate in a specific frequency range but still want to produce haptic waveforms. (Adapted from [Azom.com](https://www.azom.com/article.aspx?ArticleID=15670))

Use DC to power the LRA's in the Physical Computing lab as they come with a built in driver that converts DC to AC.

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/vibration.drawio.svg" alt="Vibration motor schematic"> <figcaption style="text-align:center"><em>Vibration motor schematic </em></figcaption></figure>

The above circuit uses a [transistor](https://guides.ioref.org/parts/2222) to switch the motor on and off.


```
const int MOTORPIN = 5;

void setup()
{
  pinMode(MOTORPIN, OUTPUT);
}

void loop()
{
  digitalWrite(MOTORPIN, HIGH);
  delay(1000);
  digitalWrite(MOTORPIN, LOW);
  delay(1000);
}
```

## Resources

- https://www.precisionmicrodrives.com/vibration-motors/coin-vibration-motors/
