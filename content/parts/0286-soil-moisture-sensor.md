---
title: soil moisture sensor
description: soil moisture sensor
category: input
signal_type: Continuous
image: moisturesensor.jpeg
inventory_group: environment
parts:
- number: 0286
---

## About

The SparkFun Soil Moisture Sensor is a simple breakout for measuring the moisture in soil and similar materials. The soil moisture sensor is pretty straight forward to use. The two large exposed pads function as probes for the sensor, together acting as a variable resistor. The more water that is in the soil means the better the conductivity between the pads will be and will result in a lower resistance, and a higher SIG out.

You'll need to connect the VCC and GND pins to power and ground on your Arduino, as well as connect SIG to an analog input (A-prefixed) pin, and you will receive a SIG out which will depend on the amount of water in the soil. A simple 3-pin screw pin terminal or a 3-pin jumper wire assembly can be soldered onto the sensor for easy wiring. (Adapted from [Sparkfun](https://www.sparkfun.com/products/13322))
