---
title: Ultrasonic Ranger
description: Measures distance
category: input
subcategory: proximity
signal_type: Continuous
image: 0572.jpg
related:
- infrared-proximity-sensor-qrd1114
- active-buzzer
- passive-buzzer
parts:
- number: '0572'
---

## What it is

An ultrasonic ranger (or ultrasonic proximity sensor) is a short- to medium- range proximity sensor.

## When to use it

When you need to measure distance to an object from a few inches to a few feet away. It can also be used to detect simple motion directly in front of it, such as a wave or walk by. Note that while multiple of these sensors may be used in one project, they cannot sense simultaneously or they will interfere with each other.

## How it works

The ultrasonic ranger works very similar to a bat's echolocation or the sonar system found on boats and submarines. It emits an ultrasonic chirp at roughly 40,000 Hz (inaudible to humans) and listens for an echo or reflection of the chirp. The time it takes between the chirp and the reply indicates the distance between the sensor and an object.

<figure class="image" style="text-align:center">   <img src="/images/parts/0572_sonar1.svg" alt="Sonar Diagram">   <figcaption style="text-align:center"><em>Image from author Georg Wiora via <a href="https://upload.wikimedia.org/wikipedia/commons/0/07/Sonar_Principle_EN.svg">Wikimedia Commons</a></em></figcaption></figure>


Sometimes a faint click or tapping sound can be heard; this is the sound of the ultrasonic chirp bouncing off of objects at lower frequencies.

## How to use it

The ultrasonic ranger is simple to connect. Connect `GND` to ground and `VCC` to 5V. The trigger and echo pins connect to two digital pins. The trigger pins tells the ranger when to chirp, and the echo pin indicates when the reply is heard.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0572_schematic1.svg" alt="Ultrasonic Ranger Schematic">   <figcaption style="text-align:center"><em>For this example, the ultrasonic ranger uses pins 11 and 12</em></figcaption></figure>

This code requires the NewPing library. You can install it in the Arduino IDE by going to `Sketch` > `Include Library` > `Manage Libraries` and searching for "NewPing." This library handles all of the code to trigger the ultrasonic ranger, wait for its echo reply, and convert the timings into distance.

```cpp
/*
 * This program sets up an ultrasonic ranger connected to
 * TRIGGER_PIN and ECHO_PIN and sends the data back to the
 * computer via serial.
 *
 * Initially by Tim Eckel from https://bitbucket.org/teckel12/arduino-new-ping/src/2ebf391d9be289aeb569c84115ee14705dd16d07/examples/NewPingExample/NewPingExample.pde
 * Modified 2021-04-23 by Perry Naseck
 */
#include <NewPing.h>

const int TRIGGER_PIN = 12; // Digital output pin for chirp trigger
const int ECHO_PIN = 11;    // Digital input pin for echo reply

// Maximum distance we want to ping for (in centimeters).
// Typical maximum sensor distance is rated to 100cm.
const int MAX_DIST = 100;

// Variable to keep track of the current proximity
int currentDist;

// Setup the ultrasonic ranger with the correct pins and
// maximum distance
NewPing mySonar(TRIGGER_PIN, ECHO_PIN, MAX_DIST);

void setup() {
  // Setup serial port to send the current proximity back to the computer
  Serial.begin(9600);
}

void loop() {
  // Get the ultrasonic ranger distance
  // Can also use mySonar.ping_in() for inches
  currentDist = mySonar.ping_cm();

  // Send the data over serial
  Serial.print("Ping (cm): ");
  Serial.println(currentDist); // Send ping, get distance in cm and print result (0 = outside set distance range)

  // Delay to not send messages too fast.
  // In this case, delay is also to ensure that the sensor
  // is not pinged too fast. Always wait at a minimum 29ms
  // between pings.
  delay(100);
}
```

## Resources

- [NewPing Library Reference](https://bitbucket.org/teckel12/arduino-new-ping/wiki/Home)
- [60-223 Ultrasonic Ranger Reference](https://courses.ideate.cmu.edu/60-223/f2020/tutorials/ultrasonic-ranger)
