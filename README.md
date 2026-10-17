# Nova.
Using Voice command for play music.just.
you need MPD

A lightweight, local-first voice assistant for controlling MPD (Music Player Daemon) with your voice. 

## Architecture
- **Client** (`nova.py`): Captures audio from your microphone and sends it to the server.
- **Server** (`server.py`): Runs Whisper (OpenAI) to transcribe audio into text and returns the command.

## Requirements
- NixOS (for client) with `mpd`, `sounddevice`, `python-mpd2`.
- Python 3 with `flask`, `openai-whisper` (for server).
- MPD running locally.

## How to use
1. Start the server: `python3 server.py`
2. Start the client: `python3 nova.py`
3. Say: "Вруби [название трека]"

## Why?
Because I wanted my own Nova from Serial Experiments Lain.
