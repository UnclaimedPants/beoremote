# beoremote
Bang &amp; Olufsen Arduino IR Receiver for Beo4 Remote for use with Kodi TV over JSON RPC API

## Assumptions

You have the following:

1. Arduino Uno
2. B&O IR Eye, wired to pin 10 on the Arduino Uno, 5V, GND
3. Arduino connected to Kodi host via USB
4. B&O Beo4 Remote

## Getting Started

Tested on Ubuntu 18.10:
    $ ./install.sh

## IR Receiver

This repo includes the Arduino code to listen to commands sent from a Beo4 remote to a B&O IR Eye

## Kodi Integration

This repo also includes a python daemon which listens for IR commands and sends them to Kodi TV over JSON RPC API. 

## Credits

Most of the arduino code was done by https://github.com/christianlykke9/Beomote
