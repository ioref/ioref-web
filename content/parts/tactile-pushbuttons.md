---
title: tactile button switch
description: tactile button switch, momentary, breadboard compatible
signal_type: Binary (on/off)
image: 0356.jpg
related:
- tilt-switches
- lever-switches
- relays
- pushbuttons
group: tactile-pushbuttons
---

## About

Push-button switches are the classic momentary switch, as they only remain in their "on" state as long as they’re being actuated (pressed, held, etc). (adapted from Sparkfun)

When pressed, the tactile button switches connect two points in a circuit by allowing electricity to flow through. Tactile Button Switches have four pins, which can be a little confusing, but because pins B and C are connected together as well as A and D, there are only really two electrical connections. (adapted from Adafruit)

<figure class="image" style="text-align:center"> <img src="/images/parts/push_button.png" alt="Tactile Button Switch Interior"> <figcaption style="text-align:center"><em>The interior wiring of a Tactile Button Switch | Image from <a href="https://learn.adafruit.com/adafruit-arduino-lesson-6-digital-inputs?view=all">Adafruit</a> </em></figcaption></figure>

When wiring a breadboard, the convention is for the positive and negative power lines to lie on opposite sides of the board. Therefore, the standard set-up is to place the push-button running across the middle of the breadboard, and **connect the electrical leads to A and C, or B and D**.

<figure class="image" style="text-align:center"> <img src="/images/parts/valley.jpg" alt="Button wired across the valley of the breadboard"> <figcaption style="text-align:center"><em>Button wired across the valley of the breadboard</em></figcaption></figure>

## Getting started

The below code and schematic sets up a circuit where pressing the button turns the LED on, and leaving the button off turns the LED off.

<figure class="image" style="text-align:center"> <img src="/images/parts/button example.svg" alt="schematic for code below"> <figcaption style="text-align:center"><em>schematic for code below</em></figcaption></figure>

```
const int LEDPIN = 5;
const int BUTTONPIN = 11;

void setup()
{
  pinMode(BUTTONPIN, INPUT);
  pinMode(LEDPIN, OUTPUT);
}

void loop()
{
  if (digitalRead(BUTTONPIN) == LOW)
  {
    digitalWrite(LEDPIN, LOW);
  }
  else
  {
    digitalWrite(LEDPIN, HIGH);
  }
}
```

## Resources

- https://learn.adafruit.com/adafruit-arduino-lesson-6-digital-inputs?view=all
