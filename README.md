# Sensor Dashboard - Streamlit Mockup

This repository contains a mockup version of the sensor monitoring dashboard currently in development.

## Overview

This is a prototype dashboard for visualizing environmental sensor data (temperature and noise readings). The mockup uses simulated data to demonstrate the final dashboard functionality and interface.

## Live Demo

The dashboard is publicly deployed on Streamlit Cloud:
https://csenses.streamlit.app/

## Features

- Real-time visualization of temperature and noise data
- Support for multiple sensors
- Time-based filtering and data aggregation
- Individual sensor views via URL parameters (e.g., `?sensor=10`)

## Deployment

This repository is configured for direct deployment on Streamlit Cloud. To deploy your own instance:

1. Fork this repository
2. Connect your GitHub account to Streamlit Cloud
3. Select this repository for deployment
4. Streamlit will automatically detect and deploy the app

## Data Structure

The mockup uses two CSV files:
- `data.csv` - Sensor readings with timestamps
- `metadata.csv` - Sensor metadata and locations

## Note

This is a mockup version with simulated data. The production dashboard will be hosted in Azure.