---
title: 1N4007 diode
description: Allows electricity to flow through it in only one direction. Often used with
  DC motors to prevent reverse currents from damaging components.
category: power
subcategory: power
signal_type: n/a
image: 4007.jpg
inventory_group: diodes
related:
- light-emitting-diode-led
parts:
- number: '4007'
---

## About

A diode is a two-terminal passive device that essentially acts as a one-way switch for current. Its function is to control the direction of current-flow. An ideal diode has infinite resistance in the backward direction, but zero resistance in the forward direction: thus, current passing through a diode can only go in one direction, called the forward direction. Current trying to flow the reverse direction is blocked.

## Getting started

<figure class="image" style="text-align:center"> <img src="/images/parts/diode example.svg" alt="Diode correct and incorrect schematic"> <figcaption style="text-align:center"><em>Wiring a diode correctly and incorrectly </em></figcaption></figure>

In the above schematic, if power is pushed through pin 3, the active buzzer will work as the diode is forward-biased, but if power is pushed through pin 13, the active buzzer will not work as the diode is backward-biased.

## Resources

- https://learn.sparkfun.com/tutorials/diodes/all
