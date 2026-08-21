---
title: infrared proximity sensor, QRD1114
description: Measures distance
signal_type: Continuous
image: 0236.jpg
related:
- infrared-receivers
- photoresistors
- ultrasonic-rangefinders
- leds
group: proximity-sensors
---

## What it is

An optical proximity sensor is a short-range proximity sensor.

## When to use it

When you need to measure distance to an object no more than a few inches away (1" to 8"). It can also be used to detect simple motion directly in front of it, such as a wave. Note that it does not work well outdoors or in direct sunlight.

## How it works

An infrared proximity sensor works by shining infrared (IR) light out and detecting the intensity of light reflected back. If something relatively reflective is quite close to it, then the sensor will see a strong reflection. As the object gets farther away, the intensity of the reflection will fall off. This sensor is highly susceptible to interference from external sources or reflections of infrared light, such as the sun.

This particular infrared proximity sensor consists of an infrared LED and infrared photocell aligned in one package. The clear-window side is the IR LED and the darker side is the IR photocell. The darker window is an infrared filter which allows for only infrared light to reach the photocell behind it. As the reflected infrared light becomes more intense, the resistance of the photocell drops. To learn more about photocells/photoresistors, see the [Photoresistor page](/parts/photoresistors/).

## How to use it

The infrared LED is connected to constant power through a current-limiting resistor (just like any other LED). The photocell is connected to an analog pin along with a pull-down resistor and adjustment potentiometer. The resistor and potentiometer on the photocell serve a similar purpose as the voltage divider used with the [Photoresistor (see this page for more information)](/parts/photoresistors/).

The pins on the sensor are not marked and do not vary in length, so use the diagram below to orient the sensor:

<figure class="image" style="text-align:center">   <img src="/images/parts/0236_diagram1.svg" alt="Optical Proximity Sensor Pin Diagram">   <figcaption style="text-align:center"><em>The pins on the sensor are not marked</em></figcaption></figure>

The potentiometer allows for adjusting the sensor offset for outside ambient light. If necessary, the potentiometer may be replaced with a resistor once dialed in. To calibrate the sensor, hold a reflective object (such as a piece of paper) at close and far ranges from the sensor. Turn the potentiometer such that when the paper is close or far from the sensor, the values returned by the example code below discernibly change.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0236_schematic1.svg" alt="Optical Proximity Sensor Schematic">   <figcaption style="text-align:center"><em>For this example, the proximity sensor uses pin A0</em></figcaption></figure>

```cpp
/*
 * This program reads an optical proximity sensor
 * connected to DISTANCE_PIN and sends the data back
 * to the computer via serial.
 *
 * Created 2021-04-21 by Perry Naseck
 */

// Set which analog pin on the Arduino the proximity sensor is connected to
const int DISTANCE_PIN = A0;

// A place to store the data when received
int distanceVal = 0;

void setup() {
  // Setup serial port to send the data back to the computer
  Serial.begin(9600);

  // Setup the proximity sensor analog pin as an input pin
  pinMode(DISTANCE_PIN, INPUT);
}

void loop() {
  // Get distance value from the proximity sensor
  distanceVal = analogRead(DISTANCE_PIN);

  // Send the data over serial
  Serial.println(distanceVal);

  // Delay to not send messages too fast
  delay(100);
}
```

## Resources

- [60-223 Infrared Proximity Sensor Reference](https://courses.ideate.cmu.edu/60-223/f2020/tutorials/IR-proximity-sensor)
- [LTH-1550-01 Datasheet](https://www.jameco.com/Jameco/Products/ProdDS/2202378.pdf)
