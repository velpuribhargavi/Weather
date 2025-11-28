import requests
import sqlite3
from datetime import datetime

class WeatherApp:
    def __init__(self, api_key):
        self.api_key = api_key
        self.setup_db()
    
    def setup_db(self):
        conn = sqlite3.connect('weather.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                city TEXT, temp REAL, humidity INTEGER, 
                condition TEXT, time TEXT
            )
        ''')
        conn.close()
    
    def get_weather(self, city):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            data = requests.get(url).json()
            return data if data['cod'] == 200 else None
        except:
            return None
    
    def save_data(self, data):
        conn = sqlite3.connect('weather.db')
        conn.execute(
            "INSERT INTO weather VALUES (?, ?, ?, ?, ?)",
            (data['name'], data['main']['temp'], data['main']['humidity'],
             data['weather'][0]['description'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    
    def display(self, data):
        print(f"City: {data['name']}")
        print(f"Temp: {data['main']['temp']}C")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Condition: {data['weather'][0]['description']}")
    
    def show_history(self):
        conn = sqlite3.connect('weather.db')
        for row in conn.execute("SELECT * FROM weather ORDER BY time DESC LIMIT 5"):
            print(f"{row[4]} | {row[0]:<15} | {row[1]:>5}C | {row[2]:>2}% | {row[3]}")
        conn.close()

def main():
    app = WeatherApp("e4ed6f2cb4175ca76f2f5c1d38f900c8")  # api key
    
    while True:
        print("\n1. Get Weather\n2. History\n3. Exit")     # Enter choice
        choice = input("Choice: ")
        
        if choice == '1':
            city = input("City: ")                  # Enter city name
            data = app.get_weather(city)
            if data:
                app.display(data)
                app.save_data(data)
            else:
                print("City not found")
        elif choice == '2':
            app.show_history()
        elif choice == '3':
            break

if __name__ == "__main__":
    main()
