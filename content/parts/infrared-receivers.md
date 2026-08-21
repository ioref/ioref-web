---
title: Infrared Receiver
description: Interprets infrared remote control signals.
signal_type: Continuous
image: 0251.jpg
related:
- proximity-sensors
- photoresistors
- leds
- infrared-remotes
group: infrared-receivers
---

## What it is

The infrared receiver interprets infrared light commands.

## When to use it

When you want to control your project using an [Infrared Remote](/parts/infrared-remotes/).

## How it works

Infrared (IR) communication is a common and inexpensive wireless communication technology. IR light has a slightly longer wavelength than visible light, making it undetectable to the human eye. A common use of IR communication is in television remotes.

Machines communicate with infrared light by pulsing infrared light on and off very rapidly in an exact sequence. The light pulses very fast (typically 38 kHz), and different sequences are created by varying the number of pulses and time between pulses. A machine can recognize each sequence as a piece of data or a command such as "volume up."

<figure class="image" style="text-align:center">   <img src="/images/parts/0251_graph1.jpg" alt="IR Pulse Graph">   <figcaption style="text-align:center"><em>Image from <a href="https://learn.sparkfun.com/tutorials/ir-communication/all">Sparkfun</a></em></figcaption></figure>

Infrared receivers, sometimes called IR sensors or IR detection diodes, usually come in two different form factors: as individual diodes or mounted on a small breakout board. Breakout boards usually contains a small LED that blinks every time the receiver detects a signal which can be handy for debugging.

_Adapted from [Sparkfun](https://learn.sparkfun.com/tutorials/ir-communication/all)_

## How to use it

Connect the `R` VCC pin to 5V, the `G` GND pin to ground, and the `Y` out pin to a digital pin. Use the IRremote library to interpret the digital signals (example below).

The sensor can interpret commands from the [Infrared Remote](/parts/infrared-remotes/) or most any other television remote.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0251_schematic1.svg" alt="IR Receiver Schematic">   <figcaption style="text-align:center"><em>For this example, the IR Receiver uses pin 11</em></figcaption></figure>

This code requires the IRremote library. You can install it in the Arduino IDE by going to `Sketch` > `Include Library` > `Manage Libraries` and searching for "IRremote." This library handles all of the code to convert the pulses into usable data.

```cpp
/*
 * This program receives an IR message from an IR receiver on pin
 * IR_RECEIVE_PIN and sends the data back to the computer via serial.
 *
 * Initially coded 2009 Ken Shirriff http://www.righto.com/
 * Modified 2021-01-15 by Perry Naseck
 */

#include <IRremote.h>

// Set which digital pin on the Arduino the data pin on the receiver is connected to
const int IR_RECEIVE_PIN = 11;

// Create the receiver instance using that pin
IRrecv IrReceiver(IR_RECEIVE_PIN);

// A place to store the IR data when received
decode_results results;

void setup() {
  // Setup serial port to send the IR data back to the computer
  Serial.begin(9600);

  // Start the receiver
  IrReceiver.enableIRIn();
}

void loop() {
  // Every time we loop, check if there is data to decode and store it in results
  if (IrReceiver.decode(&results)) {
    // If there is IR data, then send it to serial
    Serial.println(results.value, HEX);

    // Get ready to receive the next value
    IrReceiver.resume();
  }

  // Delay to not send messages too fast
  delay(100);
}
```

## Resources

- [Infrared Remote](/parts/infrared-remotes/)
- [Instructable: Using Infrared Sensor With Arduino](https://www.instructables.com/Using-Infrared-Sensor-With-Arduino/)
- [Sparkfun: IR Communication](https://learn.sparkfun.com/tutorials/ir-communication/all)
