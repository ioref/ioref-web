---
title: thermistor
description: thermistor, ~10kΩ resistance at 25ºC, resistance decreases as temperature increases,
  NTCLE100E3103JB0
category: input
subcategory: temperature
signal_type: Continuous (many possible values)
image: 0270.jpg
related:
- photoresistor
parts:
- number: '0270'
---

## About

Thermistors are variable resistors that change their resistance with temperature. There are two types: in Negative Temperature Coefficient (NTC) thermistors, resistance decreases with an increase in temperature; in Positive Temperature Coefficient (PTC) thermistors, resistance increases with an increase in temperature. NTC thermistors are the most common. (Adapted from CircuitBasics)

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/thermistor_schematic.svg" alt="Thermistor Schematic"> <figcaption style="text-align:center"><em>How to wire a thermistor in series with a resistor for the starter code below</em></figcaption></figure>

The below starter code was taken from Adafruit's [Using a Thermistor](https://learn.adafruit.com/thermistor/using-a-thermistor) page, and includes several sets of calculations, including some which require specs from the specific thermistor you use. As a summary:

1. The code calculates the value of the thermistor's resistance in relation to the 10KΩ resistor by using ratio calculations (a.k.a., for those familiar, the Voltage Divider formula).
2. It averages values of resistance read for a less noisy and more accurate reading. The original code also uses 3.3V as the driving voltage rather than the standard 5V due to 3.3V having less fluctuations, but this part of the code is omitted due to draw.io's restraints (as this requires a wiring set-up including the AREF pin on the Arduino UNO).
3. It also takes the raw resistance calculation and feeds it through the Steinhart-Hart Equation, which converts raw resistance to a temperature in Celsius. This step requires specific thermistor values—`THERMISTORNOMINAL` (known resistance at a standard temperature, usually room temp: 25℃), `TEMPERATURENOMINAL` (the aforementioned standard temperature in Celsius), and `BCOEFFICIENT` (a value unique to the thermistor indicating the steepness of the relation between thermistor resistance and temperature) in the code below. For the specific part kept in the physical computing lab, `THERMISTORNOMINAL` is 10KΩ, `TEMPERATURENOMINAL` is 25℃, and `BCOEFFICIENT` is 3977K. The code below is edited to reflect this.

```
// SPDX-FileCopyrightText: 2011 Limor Fried/ladyada for Adafruit Industries
//
// SPDX-License-Identifier: MIT

// Thermistor Example #3 from the Adafruit Learning System guide on Thermistors
// https://learn.adafruit.com/thermistor/overview by Limor Fried, Adafruit Industries
// MIT License - please keep attribution and consider buying parts from Adafruit

// Edited by Shenai Chan on 07/23/22

// which analog pin to connect
#define THERMISTORPIN A0
// resistance at 25 degrees C
#define THERMISTORNOMINAL 10000
// temp. for nominal resistance (almost always 25 C)
#define TEMPERATURENOMINAL 25
// how many samples to take and average, more takes longer
// but is more 'smooth'
#define NUMSAMPLES 5
// The beta coefficient of the thermistor (usually 3000-4000)
#define BCOEFFICIENT 3977
// the value of the 'other' resistor
#define SERIESRESISTOR 10000

int samples[NUMSAMPLES];

void setup(void) {
  Serial.begin(9600);
}

void loop(void) {
  uint8_t i;
  float average;

  // take N samples in a row, with a slight delay
  for (i=0; i< NUMSAMPLES; i++) {
   samples[i] = analogRead(THERMISTORPIN);
   delay(10);
  }

  // average all the samples out
  average = 0;
  for (i=0; i< NUMSAMPLES; i++) {
     average += samples[i];
  }
  average /= NUMSAMPLES;

  Serial.print("Average analog reading ");
  Serial.println(average);

  // convert the value to resistance
  average = 1023 / average - 1;
  average = SERIESRESISTOR / average;
  Serial.print("Thermistor resistance ");
  Serial.println(average);

  float steinhart;
  steinhart = average / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert absolute temp to C

  Serial.print("Temperature ");
  Serial.print(steinhart);
  Serial.println(" *C");

  delay(1000);
}
```

## Resources

- https://learn.adafruit.com/thermistor/using-a-thermistor
