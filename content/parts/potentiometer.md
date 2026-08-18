---
title: Potentiometer
description: A rotating variable resistor (knob)
category: input
subcategory: movement
signal_type: Continuous
image: 0390.jpg
inventory_group: potentiometers
related:
- photoresistor
- thermistor
- three-axis-accelerometer
- joystick-module
---

## What it is

The potentiometer is variable resistor that is adjusted with rotation (a knob).

## When to use it

When you need an adjustable knob with a finite range or when you need to measure rotation within a finite range. The potentiometer has a finite range because it may turn all the way to the left and stop and turn all the way to the right and stop.

## How it works

<figure class="image" style="text-align:center">   <img src="/images/parts/potentiometer_interior.gif" alt="Potentiometer Interior">   <figcaption style="text-align:center"><em>The interior of a potentiometer, with a resistive track, a wiper that slides along it, and two pins bracketing the track. | Image from <a href="https://fddrsn.net/pcomp/examples/potentiometers.html">Jeff Feddersen at NYU Physical Computing</a> </em></figcaption></figure>

A potentiometer is a variable resistor. The potentiometer works by sliding a wiper around a resistive track. The wiper is connected to the center pin, and the outer pins are connected to either end of the track. The closer the wiper is to either end of the track, the smaller the resistance is from the wiper to that end of the track. So, turning the potentiometer all the way to the left would mean there is no resistance between the wiper and the left pin but a lot of resistance between the wiper and the right pin. Moving the potentiometer to the center would cause there to be equal resistances between the wiper and the two pins.

## How to use it

The rotation of the potentiometer can be measured with an analog pin on an Arduino. If the left pin is connected to ground and the right pin is connected to 5V, then the middle pin (the wiper) will have a voltage that ranges from 0V to 5V as the potentiometer turns from left to right.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0390_schematic1.svg" alt="Potentiometer Schematic">   <figcaption style="text-align:center"><em>For this example, the potentiometer is connected to pin A0</em></figcaption></figure>

```cpp
/*
 * This reads a potentiometer on analog pin POTENTIOMETER_PIN
 * and sends the data back to the computer via serial.
 *
 * Created 2021-04-02 by Perry Naseck
 */

// Set which analog pin on the Arduino that the middle pin of
// the potentiometer is connected to
const int POTENTIOMETER_PIN = A0;

// A place to store the data when received
int potentiometerVal = 0;

void setup() {
  // Setup serial port to send the data back to the computer
  Serial.begin(9600);

  // Setup the potentiometer pin as an input
  pinMode(POTENTIOMETER_PIN, INPUT);
}

void loop() {
  // Get the current potentiometer state (saves a value
  // from 0 to 1023)
  potentiometerVal = analogRead(POTENTIOMETER_PIN);

  // Send the data over serial
  Serial.print("potentiometer: ");
  Serial.println(potentiometerVal);

  // Delay to not send messages too fast
  delay(100);
}

```

## Resources

- [Adafruit Learning System: Make It Change: Potentiometers](https://learn.adafruit.com/make-it-change-potentiometers)
- [Sparkfun Tutorial: Potentiometer](https://learn.sparkfun.com/tutorials/sparkfun-inventors-kit-experiment-guide---v40/circuit-1b-potentiometer)
- [Arduino: Potentiometer Tutorial](https://www.arduino.cc/en/tutorial/potentiometer)
- [Arduino: AnalogReadSerial Example](https://www.arduino.cc/en/Tutorial/BuiltInExamples/AnalogReadSerial)

 #### Panel-mount hole pattern, from [BI Technologies P160 series datasheet](https://cdn-shop.adafruit.com/product-files/562/p160.pdf) (all values are millimeters):

<img style="vertical-align: middle;" src="/images/parts/potentiometer_panel_mount_pattern.png" alt="Panel mount drawing: circle on the right with diameter of 7.5mm; circle on the left with diameter 3mm; the center to center distance is 7.8mm.">

Note that the circle on the left is a clearance hole for the side-nubbin on the face of the potentiometer, which helps it not spin freely once installed.
