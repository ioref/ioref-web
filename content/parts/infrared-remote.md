---
title: Infrared Remote
description: Sends infrared light pulses that can be read by an Infrared Receiver.
category: output
subcategory: light
signal_type: n/a
image: 4006.jpg
related:
- infrared-proximity-sensor-qrd1114
- infrared-reciever
- photoresistor
- light-emitting-diode-led
parts:
- number: '4006'
---

## What it is

The infrared (IR) remote controls devices with infrared pulses of light.

## When to use it

When you want to control a device or Arduino that is in your line-of-sight.

## How it works

When a button is pressed, a sequence of infrared light pulses is emitted from the infrared LED on the front of the remote. A different sequence is emitted for each button. These pulses of light are invisible to the human eye. This remote is no different from a TV remote.

## How to use it

The infrared remote itself does not require any setup or configuration. As long as a battery is installed, its buttons will send infrared commands when pressed.

To receive the commands and learn more about how the commands work, please see the [Infrared Receiver page](/parts/0251/).

## Getting started

Please see the [Infrared Receiver page](/parts/0251/) for starter code and connections.

## Resources

- [Infrared Receiver](/parts/0251/)
