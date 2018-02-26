# beoremote
Bang &amp; Olufsen Arduino IR Receiver for Beo4 Remote for use with Kodi TV over JSON RPC API

## Assumptions

1. Arduino Uno
2. B&O Ir Eye, wired to pin 10 (IR), 5V (+), GND (-)
3. Arduino connected to Kodi host via USB

## IR Receiver

This repo includes the Arduino code to listen to commands sent from a Beo4 remote to a B&O IR Eye

## Kodi Integration

This repo also includes a python daemon which listens for IR commands and sends them to Kodi TV over JSON RPC API. 

## Credits

Most of the arduino code was done by https://github.com/christianlykke9/Beomote
