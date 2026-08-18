---
title: Arduino Uno
description: The Arduino gets instructions from a computer and follows them as long as it
  has power. It can be an input, output, or both.
category: controller
signal_type: n/a
image: 1000.jpg
parts:
- number: '1000'
---

## How to use it

One would be best served by taking a deep dive into the official [Arduino Uno page](https://store-usa.arduino.cc/products/arduino-uno-rev3), but as a summary, let's dissect the overview given on the page:

- **Arduino Uno** is a microcontroller board based on the ATmega328P ([datasheet](http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf)). 

The Arduino Uno's "brains" are the ATmega328P microchip—this is where the logical operations necessary to execute a program are done, where the program is stored, where the Uno has its memory, and so on. 

- It has 14 digital input/output pins (of which 6 can be used as PWM outputs), 

All output pins on an Arduino Uno are digital, meaning they can only supply 5V or no volts at all. Connections can be drawn between these pins and various chips, sensors, outputs, and other electronic devices. The Arduino Uno emulates an analog output pin with its 6 PWM output pins (marked by a ~). All of these digital output pins double as digital inputs, which can receive only binary information.

- 6 analog inputs, 

The Arduino Uno has 6 input pins (prefixed by an A) which process analog information, or a continuous spectrum of data. Things like the exact value of a potentiometer's resistance can be read by these analog inputs.

In addition to the input/output pins, the Uno also has a suite of power-dedicated pins, such as ground, V(oltage)in, 5V, and 3.3V. Plus, it has three ways to transfer data: the UART communication paradigm, which operates on pins 1 and 0 to transmit and receive data; the I2C paradigm, which operates on the SDA (serial data) and SCL (serial clock) pins to transfer data between the Arduino and an external device and run the governing clock, respectively; and the SPI paradigm, which is similar to I2C, but you can use it to send data both ways simultaneously.

- a 16 MHz ceramic resonator (CSTCE16M0V53-R0), 

It has a clock which helps regulate data lines. 

- a USB connection, a power jack, 

The Uno can be programmed from your computer through its USB port, and it can also receive power from your computer through this port. However, even when disconnected fromt he computer, it can also receive power through the power jack by hooking up a battery in the range of 7V-12V.

- an ICSP header and a reset button.

The ICSP header pins are another way of programming the Uno that's less commonly used, and the reset button clears all instructions living on the board when pressed, since whenever the Uno is turned on, it remembers the last program downloaded onto it.

## Getting started

You could check out Adafruit's [Learn Arduino](https://learn.adafruit.com/ladyadas-learn-arduino-lesson-number-0) guides, or reference previous physical computing galleries of work, many of which were powered by the Uno: https://courses.ideate.cmu.edu/60-223/s2022/reference/previous-semesters !

## Resources

- [Language References](https://www.arduino.cc/reference/en/)
- [Tutorials](https://www.arduino.cc/en/Tutorial/HomePage)
- [Arduino Uno Official Page](https://store-usa.arduino.cc/products/arduino-uno-rev3)
