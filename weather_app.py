import requests
import json
import sqlite3
from datetime import datetime
import os
import sys
import time

class WeatherDatabase:
    """Class to handle SQLite database operations"""
    
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database and create table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    humidity INTEGER NOT NULL,
                    weather_condition TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    api_response TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f" Database '{self.db_name}' initialized successfully!")
            
        except sqlite3.Error as e:
            print(f" Database initialization error: {e}")
            return False
        return True
    
    def log_weather_data(self, city, temperature, humidity, weather_condition, api_response):
        """Log weather data into the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO weather_logs 
                (city, temperature, humidity, weather_condition, timestamp, api_response)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (city, temperature, humidity, weather_condition, timestamp, json.dumps(api_response)))
            
            conn.commit()
            conn.close()
            print(f" Weather data for {city} logged successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f" Database logging error: {e}")
            return False
    
    def get_all_logs(self, limit=20):
        """Retrieve all weather logs from database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT * FROM weather_logs 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            ''')
            
            logs = cursor.fetchall()
            conn.close()
            return logs
            
        except sqlite3.Error as e:
            print(f" Error retrieving logs: {e}")
            return []
    
    def clear_all_logs(self):
        """Clear all logs from database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM weather_logs')
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f" Error clearing logs: {e}")
            return False
    
    def get_logs_count(self):
        """Get total number of logs in database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weather_logs')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except sqlite3.Error as e:
            print(f" Error getting logs count: {e}")
            return 0


class WeatherAPI:
    """Class to handle weather API operations"""
    
    def __init__(self, api_key=None):
        # Use default API key if none provided
        if not api_key or api_key.strip() == "":
            self.api_key = "e4ed6f2cb4175ca76f2f5c1d38f900c8"
            print(" Using default API key")
        else:
            self.api_key = api_key.strip()
        
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.last_request_time = 0
        self.request_delay = 1  # Delay between requests in seconds
    
    def _rate_limit(self):
        """Implement rate limiting to avoid API limits"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        self.last_request_time = time.time()
    
    def get_weather_data(self, city_name):
        """Fetch weather data from OpenWeatherMap API"""
        # Validate city name
        if not city_name or not isinstance(city_name, str) or len(city_name.strip()) == 0:
            print(" Invalid city name provided")
            return None
        
        city_name = city_name.strip()
        
        # Rate limiting
        self._rate_limit()
        
        try:
            params = {
                'q': city_name,
                'appid': self.api_key,
                'units': 'metric'  # For Celsius temperature
            }
            
            print(f" Fetching weather data for: {city_name}")
            response = requests.get(self.base_url, params=params, timeout=15)
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                print(f" Weather data retrieved successfully!")
                return data
            else:
                print(f" API returned status code: {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    print(f" Error: {error_msg}")
                    
                    # Common error messages with suggestions
                    if 'city not found' in error_msg.lower():
                        print(" Suggestion: Check the city name spelling or try a different city")
                    elif 'invalid api key' in error_msg.lower():
                        print(" Suggestion: Check your API key is correct")
                    elif 'limit' in error_msg.lower():
                        print(" Suggestion: You may have exceeded API rate limits. Wait a moment and try again")
                        
                except:
                    print(f" API Error: {response.text}")
                return None
            
        except requests.exceptions.ConnectionError:
            print(" Connection Error: Please check your internet connection")
            return None
        except requests.exceptions.Timeout:
            print(" Request Timeout: The API took too long to respond")
            return None
        except requests.exceptions.RequestException as e:
            print(f" API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f" JSON decoding failed: {e}")
            return None
        except Exception as e:
            print(f" Unexpected error during API call: {e}")
            return None


class WeatherLogger:
    """Main class to coordinate weather logging application"""
    
    def __init__(self, api_key=None):
        try:
            self.weather_api = WeatherAPI(api_key)
            self.database = WeatherDatabase()
            print(" Weather Logger initialized successfully!")
        except ValueError as e:
            print(f" Configuration error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f" Failed to initialize Weather Logger: {e}")
            sys.exit(1)
    
    def display_weather_info(self, weather_data, city):
        """Display formatted weather information"""
        if not weather_data:
            print(f" No weather data available for {city}")
            return False
        
        try:
            # Check if we have the required data
            if 'main' not in weather_data or 'weather' not in weather_data:
                print(f" Incomplete weather data for {city}")
                return False
            
            temp = weather_data['main']['temp']
            feels_like = weather_data['main'].get('feels_like', temp)
            humidity = weather_data['main']['humidity']
            pressure = weather_data['main'].get('pressure', 'N/A')
            wind_speed = weather_data.get('wind', {}).get('speed', 'N/A')
            condition = weather_data['weather'][0]['description'].title()
            
            print("\n" + "="*60)
            print(f"  WEATHER INFORMATION FOR {city.upper()}")
            print("="*60)
            print(f" City: {city}")
            print(f"  Temperature: {temp}°C")
            print(f" Feels like: {feels_like}°C")
            print(f" Humidity: {humidity}%")
            print(f" Pressure: {pressure} hPa")
            print(f" Wind Speed: {wind_speed} m/s")
            print(f"  Condition: {condition}")
            print(f" Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60 + "\n")
            return True
            
        except KeyError as e:
            print(f" Error parsing weather data: Missing key {e}")
            return False
        except Exception as e:
            print(f" Error displaying weather info: {e}")
            return False
    
    def process_city(self, city_name):
        """Process weather data for a single city"""
        if not city_name or not city_name.strip():
            print(" City name cannot be empty!")
            return False
        
        city_name = city_name.strip()
        
        # Fetch weather data from API
        weather_data = self.weather_api.get_weather_data(city_name)
        
        if weather_data and weather_data.get('cod') == 200:  # Successful API response
            # Display weather information
            if self.display_weather_info(weather_data, city_name):
                # Extract data for logging
                try:
                    temperature = weather_data['main']['temp']
                    humidity = weather_data['main']['humidity']
                    weather_condition = weather_data['weather'][0]['description']
                    
                    # Log to database
                    success = self.database.log_weather_data(
                        city_name, temperature, humidity, weather_condition, weather_data
                    )
                    return success
                except KeyError as e:
                    print(f" Missing data in API response: {e}")
                    return False
        else:
            print(f" Failed to get weather data for {city_name}")
            return False
        
        return False
    
    def view_logs(self):
        """View all logged weather data"""
        try:
            logs = self.database.get_all_logs()
            
            if not logs:
                print("\n No weather logs found in the database!")
                return
            
            total_logs = self.database.get_logs_count()
            
            print("\n" + "="*90)
            print(f" WEATHER DATA LOGS (Showing latest {len(logs)} of {total_logs} total entries)")
            print("="*90)
            print(f"{'ID':<3} {'City':<15} {'Temp (°C)':<10} {'Humidity':<9} {'Condition':<18} {'Time'}")
            print("-" * 90)
            
            for log in logs:
                # Format the timestamp to show only time if it's today, full date otherwise
                log_time = log[5]
                if len(log_time) > 16:
                    display_time = log_time[11:16]  # Show only HH:MM
                else:
                    display_time = log_time
                
                print(f"{log[0]:<3} {log[1]:<15} {log[2]:<10.1f} {log[3]:<9} {log[4]:<18} {display_time}")
            
            print("="*90)
            
        except Exception as e:
            print(f"Error viewing logs: {e}")
    
    def clear_logs(self):
        """Clear all logs from database"""
        try:
            print("\n  CLEAR ALL LOGS")
            print("="*50)
            print("This will permanently delete all weather logs from the database.")
            confirm = input("Are you sure you want to continue? (yes/NO): ").strip().lower()
            
            if confirm == 'yes':
                success = self.database.clear_all_logs()
                if success:
                    print(" All logs cleared successfully!")
                else:
                    print(" Failed to clear logs.")
            else:
                print(" Operation cancelled.")
                
        except Exception as e:
            print(f" Error clearing logs: {e}")
    
    def get_weather_multiple_cities(self):
        """Get weather for multiple cities at once"""
        print("\n MULTIPLE CITIES WEATHER CHECK")
        print("="*50)
        cities_input = input("Enter city names separated by commas: ").strip()
        
        if not cities_input:
            print(" No cities entered!")
            return
        
        cities = [city.strip() for city in cities_input.split(',') if city.strip()]
        
        if not cities:
            print(" No valid city names found!")
            return
        
        print(f"\n Fetching weather for {len(cities)} cities...")
        successful_requests = 0
        
        for city in cities:
            success = self.process_city(city)
            if success:
                successful_requests += 1
        
        print(f"\n Summary: {successful_requests} out of {len(cities)} cities processed successfully!")
    
    def show_statistics(self):
        """Show statistics about logged weather data"""
        try:
            logs = self.database.get_all_logs(1000)  # Get more logs for stats
            
            if not logs:
                print("\n No data available for statistics.")
                return
            
            total_entries = len(logs)
            cities = {}
            temp_sum = 0
            humidity_sum = 0
            
            for log in logs:
                city = log[1]
                temp = log[2]
                humidity = log[3]
                
                # Count cities
                cities[city] = cities.get(city, 0) + 1
                
                # Sum for averages
                temp_sum += temp
                humidity_sum += humidity
            
            # Calculate averages
            avg_temp = temp_sum / total_entries
            avg_humidity = humidity_sum / total_entries
            
            # Most searched city
            most_searched = max(cities.items(), key=lambda x: x[1]) if cities else ("None", 0)
            
            print("\n" + "="*50)
            print(" WEATHER DATA STATISTICS")
            print("="*50)
            print(f"Total weather entries: {total_entries}")
            print(f"Different cities tracked: {len(cities)}")
            print(f"Most searched city: {most_searched[0]} ({most_searched[1]} times)")
            print(f"Average temperature: {avg_temp:.1f}°C")
            print(f"Average humidity: {avg_humidity:.1f}%")
            print("="*50)
            
            if cities:
                print("\n Cities frequency:")
                for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {city}: {count} entries")
            
        except Exception as e:
            print(f" Error generating statistics: {e}")
    
    def run(self):
        """Main application loop"""
        print("\n" + "" * 25)
        print("     WEATHER INFORMATION & DATA LOGGER")
        print("" * 25)
        print("A complete weather tracking application with data logging")
        
        while True:
            print("\n" + "="*50)
            print("MAIN MENU")
            print("="*50)
            print("1.  Get weather for a single city")
            print("2.  Get weather for multiple cities")
            print("3.  View all weather logs")
            print("4.  View statistics")
            print("5.  Clear all logs")
            print("6.  Exit")
            print("="*50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                city_name = input("Enter city name: ").strip()
                self.process_city(city_name)
                
            elif choice == '2':
                self.get_weather_multiple_cities()
                
            elif choice == '3':
                self.view_logs()
                
            elif choice == '4':
                self.show_statistics()
                
            elif choice == '5':
                self.clear_logs()
                
            elif choice == '6':
                print("\n" + "="*50)
                print(" Thank you for using Weather Logger!")
                total_logs = self.database.get_logs_count()
                print(f" Total weather entries in database: {total_logs}")
                print("Goodbye! ")
                print("="*50)
                break
                
            else:
                print(" Invalid choice! Please enter a number between 1-6.")


def setup_api_key():
    """Helper function to setup API key"""
    print("\n OPENWEATHERMAP API KEY SETUP")
    print("="*60)
    print("To use this application, you can:")
    print("1.  Use the default API key (may have rate limits)")
    print("2.  Get your own FREE API key from: https://openweathermap.org/api")
    print("3.  Leave empty to use default key")
    print("="*60)
    
    api_key = input("Enter your OpenWeatherMap API key (or press Enter for default): ").strip()
    
    if not api_key:
        print(" Using default API key")
        return None
    else:
        # Test the custom API key
        print("\n Testing your API key...")
        try:
            test_url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                print(" API key is valid and working!")
                return api_key
            else:
                error_data = response.json()
                error_msg = error_data.get('message', 'Unknown error')
                print(f" API key test failed: {error_msg}")
                print(" Falling back to default API key")
                return None
        except Exception as e:
            print(f" Error testing API key: {e}")
            print(" Falling back to default API key")
            return None


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import requests
        print(" Requests library is installed")
        return True
    except ImportError:
        print(" Requests library not found!")
        print(" Installing required dependency...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print(" Requests library installed successfully!")
            return True
        except:
            print(" Failed to install requests library.")
            print(" Please run: pip install requests")
            return False


def main():
    """Main function to run the weather application"""
    try:
        print(" Starting Weather Application...")
        print(" Checking dependencies...")
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Setup API key (optional - user can use default)
        api_key = setup_api_key()
        
        # Initialize and run the weather logger
        weather_app = WeatherLogger(api_key)
        weather_app.run()
        
    except KeyboardInterrupt:
        print("\n\n Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        print(" Please check your internet connection and try again")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()