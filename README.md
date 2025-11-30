## Real-Time Weather Information & Data Logger
A Python application that fetches real-time weather data from OpenWeatherMap API, displays weather information for user-specified cities, and logs all responses with timestamps to both SQLite database and text files.

## Project Structure

WEATHER
├── config.py
├── requirements.txt
├── weather_app.py
└── weather.db

# Features
- **Real-time Weather Data**: Fetches current weather information using OpenWeatherMap API

- **Multi-city Support**: Input multiple cities to get weather data

- **Comprehensive Display**: Shows temperature, humidity, weather conditions

- **Object-Oriented Design**: Clean, modular code using OOP principles


## Requirements

- Python 3.6+
- requests library
## Installation

1. Clone or download the project files
2. Install required dependencies:
   ```sql bash
   pip install requests
   ```
3. Get an API key from [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Generate an API key in your dashboard
   
## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    city TEXT,
    temp REAL,
    humidity INTEGER,
    condition TEXT,
    wind speed REAL,
    timestamp TEXT
)
```
## Data Storage & Logging

- **SQLite Database**: All API responses are automatically logged with timestamps

- **Persistent Storage**: Data remains available between sessions

- **Structured Logging**: Each entry includes:

- Timestamp of request

- City name searched

## User Experience
- **Interactive CLI**: Easy-to-use command-line interface

- **Input Validation**: Handles invalid city names gracefully

- **Continuous Operation**: Run multiple queries without restarting

- **Clear Display**: Formatted, readable weather information
- 
## Error Handling

- Invalid city names
- Network connectivity issues
- API rate limiting
- Database connection problems
- Invalid user inputs

**Example of Data base**

```sql
1. Get Weather
2. History
3. Exit
Choice: 1
City: Guntur
City: Guntur
Temp: 21.57C
Humidity: 71%
Condition: overcast clouds

1. Get Weather
2. History
3. Exit
Choice: 1
City: Ponnur
City: Ponnur
Temp: 23.31C
Humidity: 76%
Condition: overcast clouds
```


**Final output**

```sql

1. Get Weather
2. History
3. Exit
Choice: 2
2025-11-28 19:52:56 |
Vinukonda
| 21.750|70% |
overcast clouds
2025-11-28 19:52:37
Ponnur
23.310
76%
overcast clouds
2025-11-28 19:52:20
Guntur
21.570
71%
overcast clouds
2025-11-27 21:42:43
Mumbai
27.990|65% |
haze
2025-11-27 21:42:07
|Guntur|
21.10
81%
broken clouds
```

## Contact :
https://github.com/velpuribhargavi/@example.com
