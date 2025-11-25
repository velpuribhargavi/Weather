## Real-Time Weather Information & Data Logger
A Python application that fetches real-time weather data from OpenWeatherMap API, displays weather information for user-specified cities, and logs all responses with timestamps to both SQLite database and text files.

# Features
- **Real-time Weather Data**: Fetches current weather information using OpenWeatherMap API

- Multi-city Support: Input multiple cities to get weather data

- Comprehensive Display: Shows temperature, humidity, weather conditions

- Object-Oriented Design: Clean, modular code using OOP principles

## Project Structure

WEATHER_APP/
├── requirements.txt
├── weather_app.py
└── weather_data.db

## Data Storage & Logging

- SQLite Database: All API responses are automatically logged with timestamps

- Persistent Storage: Data remains available between sessions

- Structured Logging: Each entry includes:

- Timestamp of request

- City name searched

Complete API response data
## User Experience
- Interactive CLI: Easy-to-use command-line interface

- Input Validation: Handles invalid city names gracefully

- Continuous Operation: Run multiple queries without restarting

- Clear Display: Formatted, readable weather information
## Error Handling
- Invalid city names

- Network connectivity issues

- API rate limiting

- Database connection problems

Invalid user inputs
