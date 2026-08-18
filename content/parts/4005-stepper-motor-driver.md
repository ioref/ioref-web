---
title: Stepper Motor Driver
description: Receives motion instructions from the Arduino, and provides power to the Stepper
  Motor.
category: power
signal_type: n/a
image: 4005.jpg
related:
- 2222-transistor-pn2222
- 4003-breadboard-power-supply
- 4004-stepper-motor
parts:
- number: '4005'
---

## About

The stepper motor driver allows for controlling a stepper motor using digital pins. This module is essentially 4 transistor in one board. The transistors take the low-power signal from the inputs and repeat them at higher power to drive the stepper motor. This particular module uses the ULN2003 chip.

For more information on how a stepper motor works, please see the [Stepper Motor page](/parts/4004). For information on how a transistor works, please see the [transistor page](/parts/2222).

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/4005_schematic1.svg" alt="Stepper Motor Driver Schematic">   <figcaption style="text-align:center"><em>For this example, the Stepper Motor Driver is connected to pins 7, 8, 9, and 10</em></figcaption></figure>

This code requires the AccelStepper library. You can install it in the Arduino IDE by going to `Sketch` > `Include Library` > `Manage Libraries` and searching for "AccelStepper." This library handles all of the code to convert position instructions to steps of each stepper motor coil.

```cpp
/*
 * This program sets up a stepper motor and moves it back and
 * forth between two positions.
 *
 * Initially by Robert Zacaharias from https://courses.ideate.cmu.edu/60-223/s2020/tutorials/stepper
 * Modified 2021-02-19 by Perry Naseck
 */

#include <AccelStepper.h>

const int stepperPin1 = 7;  // Digital pin for IN1 of the stepper motor driver
const int stepperPin2 = 8;  // Digital pin for IN2 of the stepper motor driver
const int stepperPin3 = 9;  // Digital pin for IN3 of the stepper motor driver
const int stepperPin4 = 10; // Digital pin for IN4 of the stepper motor driver

// Setup the ULN2003 stepper motor driver with the correct pins
AccelStepper myStepper(AccelStepper::FULL4WIRE,
                       stepperPin1,
                       stepperPin2,
                       stepperPin3,
                       stepperPin4);

// Variables to set two positions to move between (measured in steps relative to
// the starting position):
// Since the stepper motor can turn infinitely, there is not an upper or lower
// limit. A negative number will move in the opposite direction from the starting
// point.
int pos1 = 10000; // 10000 means 50 full rotations if the motor has 200 steps/revolution
int pos2 = -273;

// Variable to keep track of where the stepper currently is
int currentPos;

void setup() {
  // Setup serial port to send the current position back to the computer
  Serial.begin(9600);

  // Set a maximum speed amd a starting acceleration
  myStepper.setMaxSpeed(1000);    // measured in steps per second
  myStepper.setAcceleration(500); // measured in steps per second squared
}

void loop() {
  // Store where the stepper currently is (number of steps from the starting point)
  currentPos = myStepper.currentPosition();

  // If the stepper has arrived at its destination
  if (myStepper.distanceToGo() == 0) {
    // Tell the computer where the stepper motor arrived at
    Serial.print("arrived at position: ");
    Serial.println(currentPos);

    if (currentPos == pos1) {
      // If the stepper is at for pos1, then go to pos2
      myStepper.moveTo(pos2);
    }
    else {
      // Otherwise, go to pos1
      myStepper.moveTo(pos1);
    }
  }

  // This function actually moves the stepper motor after the next destination has
  // been set. This should be called as often as possible so that the motor moves
  // smoothly. In this example, this function will be called every time the loop()
  // runs. This function determines if the motor should move one step and moves it
  // if it needs to. Whether or not it takes a step depends on the set speed and
  // acceleration.
  myStepper.run();
}
```

## Resources

- [Stepper Motor](/parts/4004/)
- [AccelStepper Library Reference](http://www.airspayce.com/mikem/arduino/AccelStepper/index.html)
