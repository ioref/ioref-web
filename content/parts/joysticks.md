---
title: joystick module
description: joystick module, up/down and left/right potentiometers, pushbutton click
signal_type: 'Up/down and left/right: Continuous (many possible values)'
image: 0372.jpg
related:
- lever-switches
- accelerometers
- potentiometers
- pushbuttons
group: joysticks
---

## What it is

The joystick measures the movement of a small arm on the X and Y axes.

## When to use it

When you want to provide user input with a joystick or track the movement of a plane (by attaching the plane of the joystick to it).

## How it works

The joystick is essentially two potentiometers connected to a stick. As the stick moves left and right, it rotates the X-axis potentiometer. As it moves up and down, it rotates the Y-axis potentiometer. The entire joystick is also connected to a button so that the stick may be pressed inward.

## How to use it

Simply connect 5 volts to `VCC`, ground to `GND`, and feed each of the potentiometer outputs (`Vrx` and `VRy`) to two of the analog input lines on the Arduino. Both axes of the joystick are measured simultaneously. Additionally, the button (`SW` pin) may be connected to a digital pin with a pullup resistor.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0372_schematic1.svg" alt="Joystick Schematic">   <figcaption style="text-align:center"><em>For this example, the Joystick uses pins A0, A1, and 2</em></figcaption></figure>

```cpp
/*
 * This program reads a joystick connected to JOY_X_PIN,
 * JOY_Y_PIN, and JOY_SW_PIN and sends the data back to
 * the computer via serial.
 *
 * Originally from: https://create.arduino.cc/projecthub/MisterBotBreak/how-to-use-a-joystick-with-serial-monitor-1f04f0
 * Modified 2021-01-19 by Perry Naseck
 */

const int JOY_X_PIN = A0; // Analog input pin for X movement
const int JOY_Y_PIN = A1; // Analog input pin for Y movement
const int JOY_SW_PIN = 2; // Digital input pin for button (pressing down on the joystick)

// Variables to keep track of the current positions and states
int joyXPos = 0;
int joyYPos = 0;
int joySWState = 0;

void setup() {
  // Setup serial port to send the joystick data back to the computer
  Serial.begin(9600);

  // Setup the joystick inputs
  pinMode(JOY_X_PIN, INPUT);
  pinMode(JOY_Y_PIN, INPUT);

  // The switch/button is just like a normal button, so
  // it needs a pullup resistor as well
  pinMode(JOY_SW_PIN, INPUT);
}

void loop() {
  // Get the current states
  joyXPos = analogRead(JOY_X_PIN);
  joyYPos = analogRead(JOY_Y_PIN);
  joySWState = digitalRead(JOY_SW_PIN);

  // Send the data over serial
  Serial.print("X: ");
  Serial.print(joyXPos);
  Serial.print(" Y: ");
  Serial.print(joyYPos);
  Serial.print(" SW: ");
  Serial.println(joySWState);

  // Delay to not send messages too fast
  delay(100);
}
```

## Resources

- [Arduino: How to Use a Joystick with Serial Monitor ](https://create.arduino.cc/projecthub/MisterBotBreak/how-to-use-a-joystick-with-serial-monitor-1f04f0)
