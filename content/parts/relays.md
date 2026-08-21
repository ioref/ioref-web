---
title: 5V Relay
description: Switches and isolates electrical devices
signal_type: n/a
image: 0502.jpg
related:
- lever-switches
- tactile-pushbuttons
- transistor
group: relays
---

## What it is

A relay is an electrically controlled switch.

## When to use it

When you need to switch a larger amount of power than the Arduino can handle or want to control an existing device separate from the Arduino. Note that most relays are mechanical and cannot switch more than a few times a second. A relay can be substituted for a mechanical switch in most circumstances.

## How it works

A standard relay is a magnetically-controlled switch. On one side is an electromagnetic coil. When it receives power, this coil moves the contacts of a switch on the other side of the relay.

<figure class="image">   <video controls autoplay muted loop style="width: 100% !important; height: auto !important;" src="/videos/parts/0502_operation1.webm"></video>   <figcaption style="text-align:center"><em>Video from author Simon A. Eugster via <a href="https://upload.wikimedia.org/wikipedia/commons/3/32/Relais-Finder-12A.webm">Wikimedia Commons</a></em></figcaption></figure>

The magnet switches the middle `COM` (common) pin between the `NC` (normally closed), and `NO` (normally open) pins. This can be seen in the video above where the middle pin touches the `NC` pin on the right by default but is pushed toward the `NO` pin when the control pins are turned on.

<figure class="image" style="text-align:center">   <img src="/images/parts/0502_animation1.gif" alt="Relay schematic animation">   <figcaption style="text-align:center"><em>Animation from author Cloullin via <a href="https://upload.wikimedia.org/wikipedia/commons/7/78/Relay_animation_without_flyback_diode_.gif">Wikimedia Commons</a></em></figcaption></figure>

## How to use it

The two control pins simply require a power source to activate the relay. This can be controlled with a digital pin.

The pins switched by the relay are typically `COM`, `NC`, and `NO`. These stand for common, normally closed, and normally open. Just like in the Lever Microswitch, these pins allow for two states of function: When the control pins do not receive power, the `COM` and `NC` pins are connected. When the control pins do receive power, the `COM` and `NO` pins are connected.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0502_schematic1.svg" alt="Relay Schematic">   <figcaption style="text-align:center"><em>For this example, the relay uses pin 13 and controls an LED</em></figcaption></figure>

```cpp
/*
 * This turns a relay connected to RELAY_PIN on and
 * off every 2 seconds.
 *
 * Created 2021-04-22 by Perry Naseck
 */

// Relay control pin connected to digital pin 13;
// this pin is also used by the onboard LED, so
// the LED should illuminate in time with the relay
const int RELAY_PIN = 13;

void setup() {
  // Set up the relay pin to be an output
  pinMode(RELAY_PIN, OUTPUT);
}

void loop() {
  // Turn on the relay
  digitalWrite(RELAY_PIN, HIGH);

  // Wait 1 second
  delay(1000);

  // Turn off the relay
  digitalWrite(RELAY_PIN, LOW);

  // Wait 1 second
  delay(1000);
}
```
