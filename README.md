# gnss-data-processing
Software system for GNSS data processing, USB-COM driver, NMEA parsing, Django integration, HTTP and MQTT latency experiments.

# GNSS Data Processing System

This repository contains the software implementation of a GNSS data processing system.

## Project structure

- `src/low_level_driver/` — USB-COM driver for reading raw NMEA data from a GNSS receiver.
- `src/gnss_application/` — GNSS data model, NMEA parser, logger, Django client and main processing module.
- `experiments/http_latency/` — HTTP latency measurement experiment.
- `experiments/mqtt_latency/` — MQTT latency measurement experiment.

## Main functions

The system provides:

- reading GNSS data through a USB-COM interface;
- receiving raw NMEA messages;
- validating NMEA checksums;
- parsing GGA and RMC messages;
- converting coordinates to decimal format;
- logging GNSS data to CSV and TXT files;
- sending structured GNSS data to a Django web service;
- measuring HTTP and MQTT data transmission latency.

## Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
