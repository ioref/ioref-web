---
title: Temperature and Humidity Sensor
description: Measures ambient temperature and humidity
category: input
subcategory: temperature
signal_type: Continuous
image: 0268.jpg
inventory_group: environment
related:
- 0270-thermistor
parts:
- number: 0268
---

## What it is

The DHT11 and DHT22 sensors are basic digital temperature and humidity sensors.

## When to use it

When you need to measure temperature and/or humidity of the surrounding air.

## How it works

They use a capacitive humidity sensor and a thermistor to measure the surrounding air.

The capacitive humidity sensor is a capacitor (to electrodes sandwiching a dieletric middle), except the dieletric material in this case absorbs water in the air. As the dieletric material absorbs water from the air or dries out, it changes capacitance.

<figure class="image" style="text-align:center">   <img src="/images/parts/0268_diagram1.svg" alt="Capacitor diagram">   <figcaption style="text-align:center"><em>In this capacitor, the dieletric is sensitive to humidity. Image from author inductiveload via <a href="https://commons.wikimedia.org/wiki/File:Parallel_plate_capacitor.svg">Wikimedia Commons</a></em></figcaption></figure>

The ambient temperature is sensed using a [Thermistor](/parts/0270/). Please see the [Thermistor](/parts/0270/) page for more information.

Lastly, there is a tiny integrated component (a silicon chip) that processes the humidity (capacitance) and temperature (resistance) and sends the data out to a digital pin.

## How to use it

There are two common varieties: the DHT11 and the DHT22. There are both wired up the same way, but they have some differences in function:

|       | Color           | Humidity             | Temperature                     | Sampling Rate        |
|:------|:----------------|:---------------------|:--------------------------------|:--------------------|
| DHT11 &nbsp;&nbsp;&nbsp;&nbsp;| Blue &nbsp;&nbsp;&nbsp;&nbsp;| 20-80% &plusmn; 5% &nbsp;&nbsp;&nbsp;&nbsp;| 0-50&deg;C &plusmn; 2&deg;C &nbsp;&nbsp;&nbsp;&nbsp;| Once a second        |
| DHT22&nbsp;&nbsp;&nbsp;&nbsp;| White&nbsp;&nbsp;&nbsp;&nbsp;| 0-100% &plusmn; 2-5% &nbsp;&nbsp;&nbsp;&nbsp;| -40-80&deg;C &plusmn; 0.5&deg;C &nbsp;&nbsp;&nbsp;&nbsp;| Once every 2 seconds |

Connect `VCC` to 5V and `GND` to ground. The data of both the DHT11 and the DHT22 are output on one digital pin.

The DHT11 also goes by the name AM2302.

## Getting started

<figure class="image" style="text-align:center">   <img src="/images/parts/0268_schematic1.svg" alt="DHT Schematic">   <figcaption style="text-align:center"><em>For this example, the DHT sensor uses pin 2</em></figcaption></figure>

This code requires the Adafruit DHT sensor library. You can install it in the Arduino IDE by going to `Sketch` > `Include Library` > `Manage Libraries` and searching for "DHT sensor library." This library handles all of the code to convert the DHT data into usable data.

```cpp
/*
 * This reads an DHT11 or DHT22 on pin DHT_PIN and
 * sends the data back to the computer via serial.
 *
 * Created 2021-02-28 by Perry Naseck
 */

#include <DHT.h>

// Set which digital pin on the Arduino the data pin on the DHT is connected to
const int DHT_PIN = 2;

// Create the DHT instance using that pin
// Only do this once! Ensure that only one of the next two lines is uncommented:
DHT myDHT(DHT_PIN, DHT11);   // Leave this line uncommented if using the DHT11
// DHT myDHT(DHT_PIN, DHT22);   // Leave this line uncommented if using the DHT22

// A place to store the data when received
// These are floats since they hold decimal point values
float tempC = 0;
float tempF = 0;
float humidity = 0;

void setup() {
  // Setup serial port to send the DHT data back to the computer
  Serial.begin(9600);

  // Start the DHT
  myDHT.begin();
}

void loop() {
  // Get values from the DHT sensor
  tempC = myDHT.readTemperature();
  tempF = myDHT.readTemperature(true); // Calling with "true" parameter for Fahrenheit
  humidity = myDHT.readHumidity();

  // Send the data over serial
  Serial.print("temp (C): ");
  Serial.print(tempC);
  Serial.print(" temp (F): ");
  Serial.print(tempF);
  Serial.print(" humidity (%): ");
  Serial.println(humidity);

  // Delay to not send messages too fast
  // The DHT11 will only have new values every 1 second, and the DHT22
  // will only have new data every 2 seconds. You can increase this
  // delay accordingly if you only want to see the new values as they
  // are available.
  delay(100);
}
```

## Resources

- [Adafruit Learning System: DHT11, DHT22 and AM2302 Sensors](https://learn.adafruit.com/dht)
- [Sparkfun Tutorial: RHT03 (DHT22) Humidity and Temperature Sensor Hookup Guide](https://learn.sparkfun.com/tutorials/rht03-dht22-humidity-and-temperature-sensor-hookup-guide)
- [DHT11 Datasheet](https://www.mouser.com/datasheet/2/758/DHT11-Technical-Data-Sheet-Translated-Version-1143054.pdf)
- [DHT22 Datasheet](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf)
