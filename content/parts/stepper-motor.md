---
title: Stepper Motor
description: Electrical connector to power motor and receive movement instructions from Arduino.
  Output shaft can rotate with motor continuously in either direction.
category: output
subcategory: movement
signal_type: n/a
image: 4004.jpg
related:
- potentiometer
- servo-motor
- dc-motor
- stepper-motor-driver
parts:
- number: '4004'
---

## About

A Stepper motor consists of multiple electromagnets arranged in a circle around a permanent magnet. When one of the electromagnets turns on, the permanent magnet moves to align with it. When the permanent magnet aligns with one electromagnet, it is called a full step. By turning on and off the electromagnets in the right sequence, the permanent magnet, which is coupled to the shaft of the motor, can move in steps clockwise and counterclockwise. The number of steps it takes for one resolution depends on the model of the stepper motor. The stepper motor can move infinitely in either direction.

<figure class="image" style="text-align:center">   <img src="/images/parts/4004_fullStep1.gif" alt="Stepper Motor Full Step">   <figcaption style="text-align:center"><em>The inside of a stepper motor moving in a full step</em></figcaption></figure>

The motor can also move to places in between two electromagnets by turning on two at the same time. This is called a half step.

<figure class="image" style="text-align:center">   <img src="/images/parts/4004_halfStep1.gif" alt="Stepper Motor Half Step">   <figcaption style="text-align:center"><em>The inside of a stepper motor moving in a half step</em></figcaption></figure>

In addition to half steps, there are also quarter, sixteenth, and even thirty-second steps, all of which are created by varying the strength of the magnetic field between two neighboring steps. Using smaller step sizes gives you more control over the motor’s movement at the expense of available torque and speed.

Real stepper motors don’t have just four full steps available. Instead, the most common value is 200 steps per revolution. They do this by winding the coils in a more complicated way than the simple diagrammatic ones shown above and by using cleverly designed mechanical teeth which steer the magnetic field precisely the way they want it to go. The following animation shows one flavor of stepper motor, which has four coils, going through four very small steps as the coils fire in sequence:

<figure class="image" style="text-align:center">   <img src="/images/parts/4004_realStep1.gif" alt="Stepper Motor Real Step">   <figcaption style="text-align:center"><em>The inside of a real stepper motor moving. Image from authors Wapcaplet and Teravolt via <a href="https://commons.wikimedia.org/wiki/File:StepperMotor.gif">Wikimedia Commons</a></em></figcaption></figure>

To use a stepper motor, you will usually need a [stepper motor driver](/parts/4005/) to be able to supply enough power to it.

## Getting started

Please see the [Stepper Motor Driver page](/parts/4005/) for starter code and connections.

## Resources

- [Stepper Motor Driver](/parts/4005/)
