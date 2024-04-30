import requests
import datetime
import logging
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города и я пришлю сводку погоды!")

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.reply("Для получения сводки погоды напишите название города.\n"
                        "Например: Москва, Санкт-Петербург, Лондон и т.д.\n"
                        "Чтобы получить прогноз погоды на следующий день, просто напишите название города.\n"
                        "Чтобы увидеть этот текст снова, напишите команду /help.")

@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        print("Получение данных о погоде...")
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        r.raise_for_status()
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        print("Отправка сводки погоды...")
        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
              f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
              f"***Хорошего дня!***"
              )

        print("Получение данных о прогнозе погоды...")
        forecast_r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={message.text}&appid={open_weather_token}&units=metric"
        )
        forecast_r.raise_for_status()
        forecast_data = forecast_r.json()

        forecast_city = forecast_data["city"]["name"]
        forecast_date = datetime.datetime.fromtimestamp(forecast_data["list"][0]["dt"] + 86400)
        forecast_weather = forecast_data["list"][0]["weather"][0]["main"]
        forecast_temp = forecast_data["list"][0]["main"]["temp"]

        if forecast_weather in code_to_smile:
            forecast_wd = code_to_smile[forecast_weather]
        else:
            forecast_wd = "Посмотри в окно, не пойму что там за погода!"

        print("Отправка прогноза погоды...")
        await message.reply(f"***Прогноз погоды на {forecast_date.strftime('%Y-%m-%d')}***\n"
              f"Погода в городе: {forecast_city}\nТемпература: {forecast_temp}C° {forecast_wd}\n"
              f"***Хорошего дня!***"
              )

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при обработке сообщения: {str(e)}")
        await message.reply(f"\U00002620 Проверьте название города \U00002620\n{str(e)}")
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {str(e)}")
        await message.reply(f"\U00002620 Проверьте название города \U00002620\n{str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp)
