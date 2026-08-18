---
title: Laser Distance Sensor
description: Senses distance by measuring time elapsed between sending a laser pulse and receiving
  its reflection
category: input
subcategory: proximity
signal_type: Continuous
image: laserdist.jpg
inventory_group: distance
parts:
- number: 0569
---

## About

The VL53L0X laser distance sensor held in the physical computing lab is a time of flight distance sensor. It contains a very tiny invisible laser source and a matching sensor, and it measures how long the light has taken to bounce back to the sensor. Since it uses a very narrow light source, it is good for determining distance of only the surface directly in front of it. The sensor can read distances of up to 2 meters, with an accuracy of ±3% at best to over ±10% in less optimal conditions.

Unlike sonars that bounce ultrasonic waves, the 'cone' of sensing is very narrow. And unlike IR distance sensors that try to measure the amount of light bounced, the VL53L0X is much more precise and doesn't have linearity problems or 'double imaging' where you can't tell if an object is very far or very close.

It's ready to work with most common microcontrollers, and since it speaks I2C, you can easily connect it up with SDA/SCL plus power and ground. (Adapted from [Adafruit](https://www.adafruit.com/product/3317))

For further reading, check out [Adafruit's extensive tutorial page](https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/overview) about the laser distance sensor. (Note that some specs—like measuring range—may be different as the chip in the lab is from a different manufacturer.)

## Resources

-  https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/overview
