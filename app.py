import telebot
import sqlite3
from telebot import types
from gigachat import GigaChat
import base64
from datetime import datetime
import os
from flask import Flask, request

# Словарь с соответствием классов и их расписаний
CLASS_SCHEDULES = {
    # 1-4 классы
    "1A": "https://imgur.com/a/MkD9KF7",
    "2Б": "https://imgur.com/WvXamKB",
    "3В": "https://imgur.com/fgZr6Ti",
    "4А": "https://imgur.com/yHjwyDr",
    "1Б": "https://imgur.com/hB6zBLn",
    "2В": "https://imgur.com/mv5OZJd",
    "3А": "https://imgur.com/RQqprhu",
    "4Б": "https://imgur.com/kVLseNo",
    "1В": "https://imgur.com/1vU01mh",
    "2А": "https://imgur.com/f0RUxm9",
    "3Б": "https://imgur.com/XBsQHQ0",
    "4В": "https://imgur.com/njZEWvJ",
    
    # 5-9 классы
    "5A": "https://imgur.com/ES7hbLG",
    "6Б": "https://imgur.com/TrnbFHl",
    "7В": "https://imgur.com/TqBeJwY",
    "5В": "https://imgur.com/KjweW0I",
    "6А": "https://imgur.com/undefined",
    "7Б": "https://imgur.com/ejTEzy5",
    "5Б": "https://imgur.com/DVEvnyY",
    "6В": "https://imgur.com/OTsJkUl",
    "7А": "https://imgur.com/B7Uu7pY",
    "8А": "https://imgur.com/B7Uu7pY",
    
    # 9-11 классы
    "9А": "https://imgur.com/BSQunSG",
    "10А": "https://imgur.com/B7Uu7pY",
    "11А": "https://imgur.com/B7Uu7pY",
    "8Б": "https://imgur.com/iP1wIwY",
    "9Б": "https://imgur.com/gmxjc1X",
    "10Б": "https://imgur.com/gmxjc1X",
    "11Б": "https://imgur.com/gmxjc1X"
}

# Инициализация бота
app = Flask(__name__)
bot = telebot.TeleBot('7825701501:AAGcXwKM4uI2XIwXB_wVQrxRMzZjz4fj1N0')

BACK_BUTTON = types.KeyboardButton("Вернуться в главное меню")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройки GigaChat
GIGACHAT_CREDENTIALS = "17e7bfac-6004-484b-ac8d-8b644321a445:96b9f86f-c54b-4939-81ae-232894ee003a"
GIGACHAT_CREDENTIALS_BASE64 = base64.b64encode(GIGACHAT_CREDENTIALS.encode()).decode()

def get_news_summary(title, content):
    """Генерирует объединённое описание новости без дублирования информации"""
    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS_BASE64, verify_ssl_certs=False) as giga:
            prompt = (
                "Создай краткое описание новости (2-3 предложения), объединив информацию из заголовка и текста. "
                "Не повторяй одинаковые факты. Формат:\n"
                "1. Основное событие\n"
                "2. Важные детали\n"
                "3. Даты/места (если есть)\n\n"
                f"Заголовок: {title}\n"
                f"Текст: {content[:2000]}"
            )
            response = giga.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        return f"{title}. {content[:150]}..."  # Fallback

def format_date(db_date):
    """Форматирует дату из БД в dd.mm.yyyy"""
    try:
        # Пробуем разные форматы дат
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
            try:
                date_obj = datetime.strptime(db_date, fmt)
                return date_obj.strftime('%d.%m.%Y')
            except ValueError:
                continue
        return db_date  # Если ни один формат не подошел
    except Exception as e:
        print(f"Ошибка форматирования даты {db_date}: {e}")
        return db_date

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_news = types.KeyboardButton('Новости')
    btn_announcements = types.KeyboardButton('Объявления')
    btn1 = types.KeyboardButton('Расписания')
    btn2 = types.KeyboardButton('Заявления')
    btn3 = types.KeyboardButton('Справки')
    markup.add(btn3, btn1, btn2, btn_news, btn_announcements)
    bot.send_message(message.chat.id, 'Привет! Чем я могу помочь?', reply_markup=markup)

# Обработчик новостей
@bot.message_handler(func=lambda message: message.text == 'Новости')
def show_news(message):
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # Пробуем разные варианты сортировки
        try:
            cursor.execute('SELECT title, content, day FROM news ORDER BY date(day) DESC LIMIT 5')
        except sqlite3.OperationalError:
            cursor.execute('SELECT title, content, day FROM news ORDER BY day DESC LIMIT 5')
            
        news_items = cursor.fetchall()

        if news_items:
            response = "<b>Последние новости:</b>\n\n"
            for title, content, day in news_items:
                formatted_date = format_date(day)
                summary = get_news_summary(title, content)
                
                response += (
                    f"📌 <i>{formatted_date}</i>\n"
                    f"{summary}\n\n"
                )
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Новостей пока нет.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке новостей.")
        print(f"Ошибка при обработке новостей: {e}")
    finally:
        conn.close() if 'conn' in locals() else None

# Обработчик объявлений
@bot.message_handler(func=lambda message: message.text == 'Объявления')
def show_announcements(message):
    try:
        conn = sqlite3.connect('announcements.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT title, content, day FROM announcements ORDER BY day DESC LIMIT 5')
        announcements_items = cursor.fetchall()

        if announcements_items:
            response = "<b>Последние объявления:</b>\n\n"
            for title, content, day in announcements_items:
                formatted_date = format_date(day)
                summary = get_news_summary(title, content)
                
                response += (
                    f"📌 <i>{formatted_date}</i>\n"
                    f"{summary}\n\n"
                )
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Объявлений пока нет.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке объявлений.")
        print(f"Ошибка при обработке объявлений: {e}")
    finally:
        conn.close() if 'conn' in locals() else None

@bot.message_handler(func=lambda message: message.text == "Справки")
def handle_references(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn2 = types.KeyboardButton("Об обучении")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(btn2, back)
    bot.send_message(message.chat.id, text="...", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Расписания")
def handle_schedules(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1-4 класс")
    btn2 = types.KeyboardButton("5-8 класс")
    btn3 = types.KeyboardButton("9-11 класс")
    btn4 = types.KeyboardButton("Звонки")
    btn5 = types.KeyboardButton("Внеурочная деятельность")
    back = types.KeyboardButton("Каникулы")
    abc = types.KeyboardButton("Вернуться в главное меню")
    markup.add(btn1, btn2, btn3, btn4, btn5, back, abc)
    bot.send_message(message.chat.id, text="...", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Внеурочная деятельность")
def handle_extracurricular(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1-4 классы")
    btn2 = types.KeyboardButton("5-9 классы")
    btn3 = types.KeyboardButton("9-11 классы")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(btn1, btn2, btn3, back)
    bot.send_message(message.chat.id, text="...", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Заявления")
def handle_applications(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton("Отчисление из школы")
        btn4 = types.KeyboardButton("Зачисление в 1 класс")
        btn6 = types.KeyboardButton("Льготное метро")
        abc = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn3, btn4, btn6, abc)
        bot.send_message(message.chat.id, text="...", reply_markup=markup)


# Обработчики конкретных заявлений
@bot.message_handler(func=lambda message: message.text == "Зачисление в 1 класс")
def handle_enrollment(message):
    chat_id = message.chat.id
    file_path = os.path.join(BASE_DIR, "documents", "Заявление на поступление.pdf")
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file)

@bot.message_handler(func=lambda message: message.text == "Отчисление из школы")
def handle_expulsion(message):
    chat_id = message.chat.id
    file_path = os.path.join(BASE_DIR, "documents", "Заявление на отчисление.pdf")
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file)

@bot.message_handler(func=lambda message: message.text == "Льготное метро")
def handle_metro_benefits(message):
    chat_id = message.chat.id
    file_path = os.path.join(BASE_DIR, "documents", "Заявление и анкета Метро")
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file)

# Обработчик возврата в главное меню
@bot.message_handler(func=lambda message: message.text == "Вернуться в главное меню")
def back_to_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button2 = types.KeyboardButton("Справки")
    button3 = types.KeyboardButton("Расписания")
    btn_news = types.KeyboardButton('Новости')
    btn_announcements = types.KeyboardButton('Объявления')
    btn4 = types.KeyboardButton('Заявления')
    markup.add(button2, button3, btn4, btn_announcements, btn_news)
    bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "1-4 класс")
def one_to_four(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("1A")
    button2 = types.KeyboardButton("2А")
    button3 = types.KeyboardButton("3А")
    button4 = types.KeyboardButton("4А")
    button5 = types.KeyboardButton("1Б")
    button6 = types.KeyboardButton("2Б")
    button7 = types.KeyboardButton("3Б")
    button8 = types.KeyboardButton("4Б")
    button9 = types.KeyboardButton("1В")
    button10 = types.KeyboardButton("2В")
    button11 = types.KeyboardButton("3В")
    button12 = types.KeyboardButton("4В")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10, button11, button12, back)
    bot.send_message(message.chat.id, text="...", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "5-8 класс")
def five_to_eight(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("5A")
        button2 = types.KeyboardButton("6А")
        button3 = types.KeyboardButton("7А")
        button4 = types.KeyboardButton("8А")
        button5 = types.KeyboardButton("5Б")
        button6 = types.KeyboardButton("6Б")
        button7 = types.KeyboardButton("7Б")
        button8 = types.KeyboardButton("8Б")
        button9 = types.KeyboardButton("5В")
        button10 = types.KeyboardButton("6В")
        button11 = types.KeyboardButton("7В")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10, button11, back)
        bot.send_message(message.chat.id, text="...", reply_markup=markup)

# Обработчик каникул
@bot.message_handler(func=lambda message: message.text == "Каникулы")
def handle_holidays(message):
    bot.send_photo(message.chat.id, 'https://imgur.com/yj90lFJ')

# Обработчик расписания для разных возрастных групп
@bot.message_handler(func=lambda message: message.text in ["1-4 классы", "5-9 классы", "9-11 классы"])
def handle_class_schedules(message):
    if message.text == "9-11 классы":
        bot.send_photo(message.chat.id, 'https://imgur.com/0xmzDi7')
    elif message.text == "1-4 классы":
        bot.send_photo(message.chat.id, 'https://imgur.com/GKvuDFT')
    elif message.text == "5-9 классы":
        bot.send_photo(message.chat.id, 'https://imgur.com/L75lttB')
# Обработчик звонков
@bot.message_handler(func=lambda message: message.text == "Звонки")
def handle_bells(message):
    bot.send_photo(message.chat.id, 'https://imgur.com/yKijwkz')

@bot.message_handler(func=lambda message: message.text == "9-11 класс")
def nine_to_eleven(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("9A")
    button2 = types.KeyboardButton("10А")
    button3 = types.KeyboardButton("11А")
    button5 = types.KeyboardButton("9Б")
    button6 = types.KeyboardButton("10Б")
    button7 = types.KeyboardButton("11Б")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(button1, button2, button3, button5, button6, button7, back)
    bot.send_message(message.chat.id, text="...", reply_markup=markup)

# Обработчик для всех классов
@bot.message_handler(func=lambda message: message.text in CLASS_SCHEDULES)
def handle_class_schedule(message):
    photo_url = CLASS_SCHEDULES[message.text]
    if photo_url != "https://imgur.com/undefined":  # Проверка на нерабочую ссылку
        bot.send_photo(message.chat.id, photo_url)
    else:
        bot.send_message(message.chat.id, "Извините, расписание временно недоступно")
# Запуск бота
bot.polling(non_stop=True)

# Роут для проверки работы
@app.route('/')
def home():
    return "Hello from Flask"

# Роут для установки вебхука
@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    webhook_url = f'https://soniaai331.pythonanywhere.com/{bot.token}'
    bot.set_webhook(url=webhook_url)
    return "Вебхук установлен!"

# Обработчик апдейтов от Telegram
@app.route(f'/{bot.token}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.json)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == '__main__':
    app.run()