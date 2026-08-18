---
title: H-Bridge Motor Driver
description: Receives motion instructions from the Arduino, and allows 2 motors to rotate
  both ways.
category: output
subcategory: movement
signal_type: n/a
image: 1258.jpg
inventory_group: drivers
parts:
- number: '1258'
---

## About

A H-bridge is an electronic circuit that switches the polarity of a voltage applied to a load. These circuits are often used in robotics and other applications to allow DC motors to run forwards or backwards. (Adapted from [Wikipedia](https://en.wikipedia.org/wiki/H-bridge))

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/h bridge schematic.svg" alt="Dual H Bridge Schematic"> <figcaption style="text-align:center"><em>Dual H Bridge schematic </em></figcaption></figure>
 
This monster of a diagram actually isn't too bad when you take a closer look. The pins in the upper right and lower left corners (logic and motor power) must always have power for the circuit to work (they supply power to the internal chip computer and the motors, respectively). The enable pins (upper left and lower right) are also connected to power to allow the motors to go on (if motor 1's enable is LOW, it won't spin no matter what, and the same applies to motor 2). 

The leads of the DC motors must be connected to their output pins (motor 1 has both leads to motor 1 output pins, and the same applies to motor 2). All 4 signal pins (motor 1 A, motor 1 B, motor 2 A, and motor 2 B) must be connected to digital output pins on the arduino. These are a bit trickier, but they dictate the polarity of voltage and therefore the direction of rotation. The A and B pins must be a HIGH/LOW pair for the motor to spin—supplying HIGH to both or LOW to both won't make the motor spin; but having A be HIGH and B be LOW will make the motor spin in the opposite direction than if B was HIGH and A was LOW.

Here is some simple sample code using wiring shown in the above schematic to move the motors in alternating directions:

```c
/*
  Simple H-bridge driver demo

  Drives two motors in alternating directions

  Pin mapping:

  Arduino pin | role  | description
  ----------- | ----- | ------------
  2             output  motor 2 signal A
  3             output  motor 2 signal B
  7             output  motor 1 signal B
  12            output  motor 1 signal A

  Relased to the public domain by the author

  Robert Zacharias, rzachari@andrew.cmu.edu
  Sep. 2025
*/

// set up pin numbers
const int MOTOR2APIN = 2,
          MOTOR2BPIN = 3,
          MOTOR1BPIN = 7,
          MOTOR1APIN = 12;

void setup() {
  pinMode(MOTOR2APIN, OUTPUT);
  pinMode(MOTOR2BPIN, OUTPUT);
  pinMode(MOTOR1BPIN, OUTPUT);
  pinMode(MOTOR1APIN, OUTPUT);
}

void loop() {
  // drive motor 1 in some direction
  digitalWrite(MOTOR1APIN, HIGH);
  digitalWrite(MOTOR1BPIN, LOW);
  // drive motor 2 in opposite direction
  digitalWrite(MOTOR2APIN, LOW);
  digitalWrite(MOTOR2BPIN, HIGH);

  delay(2000); // do the above for two seconds

  // drive motor 1 in different direction from before
  digitalWrite(MOTOR1APIN, LOW);
  digitalWrite(MOTOR1BPIN, HIGH);
  // drive motor 2 in different direction from before
  digitalWrite(MOTOR2APIN, HIGH);
  digitalWrite(MOTOR2BPIN, LOW);

  delay(2000); // do the above for two seconds

  // stop both motors by turning all outputs low
  digitalWrite(MOTOR1APIN, LOW);
  digitalWrite(MOTOR1BPIN, LOW);
  digitalWrite(MOTOR2APIN, LOW);
  digitalWrite(MOTOR2BPIN, LOW);

  delay(1000); // do the above for one second
}
```
