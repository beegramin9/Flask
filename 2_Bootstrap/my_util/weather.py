import requests


def get_weather(lat=37.550966, lng=126.849532):
    # 모듈을 불러오는 app.py 기준으로 상대경로를 지정해야 함
    key_fd = open('./keys/openweatherkey.txt', mode='r')
    weather_key = key_fd.read(100)
    print(weather_key)
    key_fd.close()

    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={weather_key}&units=metric&'
    result = requests.get(url).json()

    # description
    desc = result['weather'][0]['description']

    # icon
    icon_code = result['weather'][0]['icon']
    icon_url = f'http://openweathermap.org/img/w/{icon_code}.png'

    # temperature
    temp = round(result['main']['temp']+0.01, 1)
    temp_min = result['main']['temp_min']
    temp_max = result['main']['temp_max']

    html = f'''<img src="{icon_url}" height="32"> <strong>{desc}</strong>, 
                온도: <strong>{temp}&#8451</strong>, {temp_min}/{temp_max}&#8451'''

    return html
