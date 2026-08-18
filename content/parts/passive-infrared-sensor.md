---
title: Passive Infrared Sensor
description: Detects motion (of bodies that emit infrared radiation, for example, humans)
category: input
subcategory: movement
signal_type: Binary
image: IRmotion.jpg
parts:
- number: '0574'
---

## About

The passive infrared sensor detects human motion by reading the infrared radiation given off.

A PIR sensor consists of two main parts:

- A pyroelectric sensor, which consists of a window with two rectangular slots and is made of a material (typically coated silicon) that allows infrared radiation to pass through.
- A special lens called a fresnel lens which focuses the infrared signals on the pyroelectric sensor.

<figure class="image" style="text-align:center"> <img src="/images/parts/IRmotiondiagram.jpg" alt="Diagram of PIR sensor with sensitivity, delay, and trigger settings, as well as a pinout"> <figcaption style="text-align:center"><em>Diagram of PIR sensor with sensitivity, delay, and trigger settings, as well as a pinout | Image from <a href="https://www.amazon.com/gp/product/B012ZZ4LPM">Amazon</a> </em></figcaption></figure>

The above diagram shows various ways to customize the sensor. When viewing the orange shafts head-on with the fresnel lens on top, the leftmost shaft dictates the amount of time that the sensor will stay HIGH after sensing motion, with a range of 3 seconds to 5 minutes. The rightmost shaft dictates sensor range sensitivity, with a range of 3 meters to 7 meters. The orange cap on the chip can also be moved between one of two positions: single trigger, which starts time delay immediately upon seeing motion and does not sense continuous motion, and repeated trigger, which starts time delay again and again at any sensed motion. 

The +/- pins must be connected to power and ground, and the OUT pin must be connected to a digital input pin, and conveys whether motion is detected or not.

## Resources

- https://www.makerguides.com/hc-sr501-arduino-tutorial/
- https://lastminuteengineers.com/pir-sensor-arduino-tutorial/
