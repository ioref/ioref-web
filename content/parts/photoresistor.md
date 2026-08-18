---
title: photoresistor
description: photoresistor, cadmium sulfide, resistance decreases as light level increases
category: input
subcategory: light
signal_type: Continuous
image: 0260.jpg
related:
- infrared-proximity-sensor-qrd1114
- light-emitting-diode-led
parts:
- number: '0260'
---

## What it is

The photoresistor measures the amount of light hitting it. It is also called a photocell.

## When to use it

The photoresistor can measure ambient light (i.e. if the lights are on in a room, if the sensor is covered or not) or the amount of light from a specific source (i.e. LED, laser).

A normal photoresistor does not measure infrared light, but infrared photoresistors are available. Please see the [Optical Proximity Sensor](/parts/0236) page for an example of using infrared photoresistors to detect distance.

## How it works

The photoresistor's resistance changes based on the amount of light hitting it. The surface of the photoresistor has a photoconductive material between the two pins. This material changes resistance as more or fewer photons hit it. The photoresistor has a higher resistance the less light that hits it (darker = more resistance).

## How to use it

The photoresistor should be hooked up as a voltage divider with the photoresistor making up one leg of the voltage divider. So, there is a resistor (in this case typically 5.6k&#8486;) connected between 5V and the analog pin, and the photoresistor is connected between the same analog pin and ground.

The photoresistor does not have a polarity; it does not matter which way the pins are oriented.

The voltage divider circuit makes the photoresistor more reliable to measure. It ensures that the voltage the analog pin reads is always between 0V and 5V. If the photoresistor is connected directly between 5V and the analog pin, then as the resistance of the sensor gets very high (when the sensor is dark), it would have the same effect as disconnecting the from the analog pin. When an pin is "floating" like this, it will return unpredictable values. This can be tested by running the code below with nothing plugged into the analog pin; it will show random values.

The value of the added resistor can be changed to get difference ranges of sensitivity out of the photoresistor. The 5.6k&#8486; resistor is a middle-of-the-line value. For more sensitivity between "bright" and "really bright," use a 1k&#8486; resistor. For more sensitivity in darker ranges, use a 10k&#8486; resistor. These changes should only be made after first trying with the 5.6k&#8486; resistor.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0260_schematic1.svg" alt="Photoresistor Schematic">   <figcaption style="text-align:center"><em>For this example, the photoresistor uses pin A0</em></figcaption></figure>

```cpp
/*
 * This program reads a photoresistor connected to
 * PHOTORESISTOR_PIN and sends the data back to the
 * computer via serial.
 *
 * Created 2021-02-28 by Perry Naseck
 */

// Set which analog pin on the Arduino the photoresistor is connected to
const int PHOTORESISTOR_PIN = A0;

// A place to store the data when received
int lightVal = 0;

void setup() {
  // Setup serial port to send the data back to the computer
  Serial.begin(9600);

  // Setup the photoresistor analog pin as an input pin
  pinMode(PHOTORESISTOR_PIN, INPUT);
}

void loop() {
  // Get light value from the photoresistor
  lightVal = analogRead(PHOTORESISTOR_PIN);

  // Send the data over serial
  Serial.println(lightVal);

  // Delay to not send messages too fast
  delay(100);
}
```

## Resources

- [60-223 Photoresistor Reference](https://courses.ideate.cmu.edu/60-223/f2020/tutorials/reading-a-photoresistor)
- [Adafruit Learning System: Photocells](https://learn.adafruit.com/photocells)
- [Sparkfun Tutorial: Photocell Hookup Guide](https://learn.sparkfun.com/tutorials/photocell-hookup-guide/all)
- [SEN-09088 Photocell Datasheet](http://cdn.sparkfun.com/datasheets/Sensors/LightImaging/SEN-09088.pdf)
