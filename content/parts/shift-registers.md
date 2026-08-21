---
title: Shift Register (74HC595)
description: 'Has three inputs and eight outputs: allows the Arduino to control many outputs
  at once without as many pins as it would otherwise need.'
signal_type: n/a
image: 4008.jpg
group: shift-registers
---

## About

A shift register is a device that allows additional inputs or outputs to be added to a microcontroller.

This is accomplished by converting data between parallel and serial formats. A microprocessor communicates with a shift register using serial information, and the shift register gathers or outputs information in a parallel (multi-pin) format.

Shift registers come in two basic types, either SIPO, Serial-In-Parallel-Out, or PISO, Parallel-In-Serial-Out. The 74HC595 Shift Register is a SIPO and is useful for controlling a large number of outputs, including LEDs, while the latter type, PISO, is good for gathering a large number of inputs, like buttons. (Sourced from Sparkfun)

## Getting started

```
/*Shift Register
*
*Adafruit Arduino - Lesson 4. 8 LEDs and a Shift Register Shift Register
*
*https://learn.adafruit.com/adafruit-arduino-lesson-4-eight-leds/overview
*
*/

int latchPin = 5;
int clockPin = 6;
int dataPin = 4;

byte leds = 0;

void setup()
{
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
}

void loop()
{
  leds = 0;
  updateShiftRegister();
  delay(500);
  for (int i = 0; i < 8; i++)
  {
    bitSet(leds, i);
    updateShiftRegister();
    delay(500);
  }
}

void updateShiftRegister()
{
   digitalWrite(latchPin, LOW);
   shiftOut(dataPin, clockPin, LSBFIRST, leds);
   digitalWrite(latchPin, HIGH);
}
```

## Resources

- https://learn.sparkfun.com/tutorials/shift-registers/all
