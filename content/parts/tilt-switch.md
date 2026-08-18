---
title: tilt switch
description: tilt switch, ball connects the legs when can is tilted downwards
category: input
subcategory: orientation
signal_type: Binary (on/off)
image: 0272.jpg
related:
- small-lever-microswitch
- tactile-button-switch
- 5v-relay
- arcade-push-button
parts:
- number: '0272'
---

## About

<figure class="image" style="text-align:center"> <img src="/images/parts/tilt_switch.jpeg" alt="Tilt Switch Interior"> <figcaption style="text-align:center"><em>The interior of a tilt switch. | Image from <a href="https://forum.ausrocketry.com/viewtopic.php?t=6191/">Ausrocketry</a> </em></figcaption></figure>

Tilt sensors allow you to detect orientation or inclination. They are usually made by a cavity of some sort (cylindrical is popular, although not always) and a conductive free mass inside, such as a blob of mercury or rolling ball. One end of the cavity has two conductive elements (poles). When the sensor is oriented so that that end is downwards, the mass rolls onto the poles and shorts them, acting as a switch throw. (Sourced from Adafruit)

## How to use it

Attach your voltage and ground wires to the leads. Experiment with moving the switch around—with the given starter code, you can see when the conductive mass inside has rolled to connect the leads (shorting the switch), and when it's rolled away from the leads (opening the switch).

## Getting started

```
/* Better Debouncer
 *
 * This debouncing circuit is more rugged, and will work with tilt switches!
 *
 * http://www.ladyada.net/learn/sensor/tilt.html
 */

int inPin = 2;         // the number of the input pin
int outPin = 13;       // the number of the output pin

int LEDstate = HIGH;      // the current state of the output pin
int reading;           // the current reading from the input pin
int previous = LOW;    // the previous reading from the input pin

// the following variables are long because the time, measured in milliseconds,
// will quickly become a bigger number than can be stored in an int.
long time = 0;         // the last time the output pin was toggled
long debounce = 50;   // the debounce time, increase if the output flickers

void setup()
{
  pinMode(inPin, INPUT);
  digitalWrite(inPin, HIGH);   // turn on the built in pull-up resistor
  pinMode(outPin, OUTPUT);
}

void loop()
{
  int switchstate;

  reading = digitalRead(inPin);

  // If the switch changed, due to bounce or pressing...
  if (reading != previous) {
    // reset the debouncing timer
    time = millis();
  }

  if ((millis() - time) > debounce) {
     // whatever the switch is at, its been there for a long time
     // so lets settle on it!
     switchstate = reading;

     // Now invert the output on the pin13 LED
    if (switchstate == HIGH)
      LEDstate = LOW;
    else
      LEDstate = HIGH;
  }
  digitalWrite(outPin, LEDstate);

  // Save the last reading so we keep a running tally
  previous = reading;
}
```

## Resources

- https://learn.adafruit.com/tilt-sensor/using-a-tilt-sensor
