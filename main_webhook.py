import telebot
from data import DbHelper
import datetime
import time
import config
import flask
import sys
from valid_functions import *
import telegram

try:
    public_url = sys.argv[1]
except Exception as e:
    public_url = ''
    print('You did not enter the ngrok public url')
    raise e

API_TOKEN = config.TOKEN
APP_HOST = '127.0.0.1'
APP_PORT = '8444'
WEB_HOOK_URL = public_url

TOKEN = config.TOKEN


bot = telebot.TeleBot(TOKEN)
app = flask.Flask(__name__)


back = telebot.types.InlineKeyboardMarkup()
back.add(telebot.types.InlineKeyboardButton('Назад', callback_data='help'))

VALID_ARR = [chr(i) for i in range(1072, 1104)] + [chr(i) for i in range(1040, 1072)]


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет! Я бот МЭИ, помогу записаться на мероприятие.')
    if not db.person_in_db(message.chat.id):
        bot.send_message(message.chat.id, 'Введите ваше имя: ')
        bot.register_next_step_handler(message, add_name)
    else:
        help_command(message)


def add_name(message):
    name = message.text
    answer = check_valid_str(name)
    if answer is True:
        bot.send_message(message.chat.id, 'Введите вашу фамилию: ')
        bot.register_next_step_handler(message, add_surname, name)
    else:
        bot.send_message(message.chat.id, answer)
        bot.register_next_step_handler(message, add_name)


def add_surname(message, name):
    surname = message.text
    answer = check_valid_str(surname)
    if answer is True:
        bot.send_message(message.chat.id, 'Введите номер учебной группы: ')
        bot.register_next_step_handler(message, add_group_number, name, surname)
    else:
        bot.send_message(message.chat.id, answer)
        bot.register_next_step_handler(message, add_surname, name)


def add_group_number(message, name, surname):
    group_num = message.text
    answer = check_group_number(group_num)
    if answer is True:
        group_num = message.text
        db.add_person(message.chat.id, name, surname, group_num)
        help_command(message)
    else:
        bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.clear_step_handler(message)
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.if_admin(message.chat.id):
        keyboard.add(telebot.types.InlineKeyboardButton('Добавить мероприятие', callback_data='new_event'))
        keyboard.add(telebot.types.InlineKeyboardButton('Добавить админа', callback_data='add_admin'))
        keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть, кто записался на мероприятие',
                                                        callback_data='show_guests'))
    keyboard.add(telebot.types.InlineKeyboardButton('Правила аренды площадки', callback_data='show_rules'))
    keyboard.add(telebot.types.InlineKeyboardButton('Записаться на мероприятие', callback_data='registration_event'))
    keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть ближайшие мероприятия', callback_data='show_events'))
    keyboard.add(telebot.types.InlineKeyboardButton('Посмотреть мои записи', callback_data='show_my_registrations'))
    bot.send_message(message.chat.id, 'Список команд: ', reply_markup=keyboard)


def show_rules(message):
    bot.edit_message_text('Правила аренды:\n'
                          '1) На мероприятии должны соблюдаться нормы этики и морали.\n'
                          '2) Мероприятие должно быть полезно для студентов.\n'
                          '3) Запрещено проводить коммерческие выступления.\n'
                          '4) Площадка является территорией МЭИ, поэтому должны '
                          'соблюдаться правила поведения на территории учебного заведения.\n'
                          '5) Если спикер не имеет пропуск на территорию МЭИ, нужно запросить служебную записку, '
                          'чтобы он мог зайти на площадку.\n'
                          '6) Ответственный за площадку Власов Вячеслав Александрович. '
                          'По всем вопросам, связанными с арендой площадки вы можете обращаться к нему.'
                          , message.chat.id, message.message_id, reply_markup=back)


def add_admin(message):
    bot.send_message(message.chat.id, 'Отлично, давайте добавим нового админа. \n'
                                      '1) Для этого отправьте ссылку @mpei_registration_event_bot человеку\n'
                                      'Если зайти на неё из приложение Телеграм, то откроется чат со мной) '
                                      'Нужно, чтобы человек обязательно нажал на команду /start \n'
                                      '2) Перешлите мне любое сообщение от этого человека, чтобы я мог открыть '
                                      'ему функционал админа', reply_markup=back)
    bot.register_next_step_handler(message, add_admin_in_db)


def add_admin_in_db(message):
    try:
        # Расширенные настройки приватности
        if not message.forward_from:
            tg_id = int(message.text)
            if db.if_admin(tg_id):
                bot.send_message(message.chat.id, "Этот человек уже обладает функционалом админа.", reply_markup=back)
            else:
                db.add_admin(tg_id)
                bot.send_message(message.chat.id, f"Человек с идентефикатором {tg_id}"
                                                  f" успешно добавлен(a) в систему! 🥳", reply_markup=back)
                key = telebot.types.InlineKeyboardMarkup()
                key.add(telebot.types.InlineKeyboardButton('Посмотреть функционал', callback_data='help'))
                bot.send_message(tg_id, f"{message.from_user.first_name} "
                                        f"{message.from_user.last_name} добавил(а) "
                                        f"вас в систему. Теперь вам доступен функционал админа. ",
                                 reply_markup=key)
        elif db.if_admin(message.forward_from.id):
            bot.send_message(message.chat.id, "Этот человек уже обладает функционалом админа.", reply_markup=back)
        else:
            db.add_admin(message.forward_from.id)
            bot.send_message(message.chat.id, f"{message.forward_from.first_name} {message.forward_from.last_name}"
                                              f" успешно добавлен(a) в систему! 🥳", reply_markup=back)
            key = telebot.types.InlineKeyboardMarkup()
            key.add(telebot.types.InlineKeyboardButton('Посмотреть функционал', callback_data='help'))
            bot.send_message(message.forward_from.id, f"{message.from_user.first_name} "
                                                      f"{message.from_user.last_name} добавил(а) "
                                                      f"вас в систему. Теперь вам доступен функционал админа. ",
                             reply_markup=key)
    except (ValueError, TypeError, AttributeError):
        bot.send_message(message.chat.id, "Это не похоже на пересланное сообщение. Попробуйте ещё раз. "
                                          "Если вы уверены в том, что сообщение переслано от человека, "
                                          "то попробуйте другой способ:\n"
                                          "1) Oтправьте ссылку @mpei_registration_event_bot человеку\n"
                                          "Если зайти на неё из приложение Телеграм, то откроется чат со мной) "
                                          "Нужно, чтобы человек обязательно нажал на команду /start \n"
                                          "2) Пусть человек отправит вам свой идентефикатор в телеграмме. "
                                          "Найти его очень просто. Нужно написать боту @getmyid_bot и он отправит "
                                          "вам ваш идентефикатор.\n "
                                          "3) Ну а теперь вы должны отправить этот идентефикатор мне",
                         reply_markup=back)
        bot.register_next_step_handler(message, add_admin_in_db)


def new_event(message):
    bot.edit_message_text('Введите название мероприятия: ', message.chat.id, message.message_id, reply_markup=back)
    bot.register_next_step_handler(message, event_name)


def event_name(message):
    name = message.text
    answer = check_valid_str(name)
    if answer is True:
        bot.send_message(message.chat.id, 'Введите количество человек, которые могут посетить мероприятие: ',
                         reply_markup=back)
        bot.register_next_step_handler(message, event_count, name)
    else:
        bot.send_message(message.chat.id, answer, reply_markup=back)
        bot.register_next_step_handler(message, event_name)


def event_count(message, name):
    try:
        count = int(message.text)
        bot.send_message(message.chat.id, 'Введите дату в формате дд.мм.гггг ', reply_markup=back)
        bot.register_next_step_handler(message, event_day, name, count)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите количество человек, которые могут посетить мероприятие: ',
                         reply_markup=back)
        bot.register_next_step_handler(message, event_count, name)


def event_day(message, name, count):
    day = message.text
    answer = check_date(day)
    if answer is True:
        day = '-'.join(message.text.split('.')[::-1])
        bot.send_message(message.chat.id, 'Введите время начала мероприятия в формате чч:мм ', reply_markup=back)
        bot.register_next_step_handler(message, event_time, name, count, day)
    else:
        bot.send_message(message.chat.id, answer, reply_markup=back)
        bot.register_next_step_handler(message, event_day, name, count)


def event_time(message, name, count, day):
    mero_time = message.text
    answer = check_time(mero_time)
    if answer is True:
        add_event(message, name, count, day, time)
    else:
        bot.send_message(message.chat.id, mero_time, reply_markup=back)
        bot.register_next_step_handler(message, event_time, name, count, day)


def add_event(message, name, count, day, mero_time):
    db.del_events()
    db.add_event(name, count, day, time)
    day = list(map(int, day.split('-')))
    key = telebot.types.InlineKeyboardMarkup()
    key.add(
        telebot.types.InlineKeyboardButton('Правила аренды площадки', callback_data='show_rules'),
        telebot.types.InlineKeyboardButton('Назад', callback_data='help')
    )
    bot.send_message(message.chat.id, f"Мероприятие '{name}' успешно записано на "
                                      f"{datetime.date(*day).strftime('%d/%m/%Y')} в {mero_time}\n"
                                      f"Незабудьте ознакомиться с правилами аренды площадки 👇",
                     reply_markup=key)


def show_events(message):
    db.del_events()
    text = ''
    events = db.show_events()
    for event in events:
        day = list(map(int, event[3].split('-')))
        text += f"{datetime.date(*day).strftime('%d/%m/%Y')} '{event[1]}' начало в {event[-1]}\n"
        text += f"Осталось мест: {event[2]}\n"
        text += '-' * 100
        text += '\n'
    if not text:
        text = 'Ближайших мероприятий нет('
    bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=back)


def registration_event(message):
    db.del_events()
    events = db.show_events()
    event_key = telebot.types.InlineKeyboardMarkup()
    if not events:
        bot.edit_message_text('Ближайших мероприятий нет( ', message.chat.id, message.message_id, reply_markup=back)
    else:
        for event in events:
            event_key.add(telebot.types.InlineKeyboardButton(event[1],
                                                             callback_data=f"add_registration_{event[0]}_"
                                                                           f"{message.chat.id}"))
        event_key.add(telebot.types.InlineKeyboardButton('Назад', callback_data='help'))
        bot.edit_message_text('Выберете мероприятие: ', message.chat.id, message.message_id, reply_markup=event_key)


def add_registration(message, event_id, telegram_id):
    db.del_events()
    if db.get_number_of_available_seats(event_id):
        if db.if_registration(event_id, telegram_id):
            bot.edit_message_text('Вы успешно записались на выступление! 🥳', message.chat.id, message.message_id,
                                  reply_markup=back)
            db.add_registration(event_id, telegram_id)
        else:
            bot.edit_message_text('Вы уже записались на это выступление', message.chat.id, message.message_id,
                                  reply_markup=back)
    else:
        bot.edit_message_text('Места закончились(', message.chat.id, message.message_id, reply_markup=back)


def show_guests(message):
    db.del_events()
    events = db.show_events()
    event_key = telebot.types.InlineKeyboardMarkup()
    if not events:
        bot.edit_message_text('Ближайших мероприятий нет( ', message.chat.id, message.message_id, reply_markup=back)
    else:
        for event in events:
            event_key.add(telebot.types.InlineKeyboardButton(event[1],
                                                             callback_data=f"show_guests_for_event_{event[0]}"))
        event_key.add(telebot.types.InlineKeyboardButton('Назад', callback_data='help'))
        bot.edit_message_text('Выберете мероприятие: ', message.chat.id, message.message_id, reply_markup=event_key)


def show_guests_for_event(message, event_id):
    guests = db.get_guests(event_id)
    text = ''
    count = 0
    for person in guests:
        count += 1
        text += f"{count}) {person[1]} {person[2]} группа {person[3]}\n"
    if text:
        bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=back)
    else:
        bot.edit_message_text('Пока никто не записался(', message.chat.id, message.message_id, reply_markup=back)


def show_my_registrations(message):
    db.del_events()
    text = ''
    events = db.get_my_registrations(message.chat.id)
    for event in events:
        day = list(map(int, event[3].split('-')))
        text += f"{datetime.date(*day).strftime('%d/%m/%Y')} '{event[1]}' начало в {event[-1]}\n"
        text += f"Осталось мест: {event[2]}\n"
        text += '-' * 100
        text += '\n'
    if not text:
        text = 'Вы ещё не записались ни на одно мероприятие('
    bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=back)


@bot.callback_query_handler(func=lambda call: True)
def all_call(call):
    if call.message:
        if call.data == 'help':
            help_command(call.message)
        if call.data == 'new_event':
            new_event(call.message)
        if call.data == 'registration_event':
            registration_event(call.message)
        if call.data == 'show_events':
            show_events(call.message)
        if call.data == 'show_rules':
            show_rules(call.message)
        if call.data == 'add_admin':
            add_admin(call.message)
        if call.data == 'show_my_registrations':
            show_my_registrations(call.message)
        if call.data == 'show_guests':
            show_guests(call.message)
        if 'add_registration_' in call.data:
            a = call.data.split('_')
            add_registration(call.message, int(a[-2]), int(a[-1]))
        if 'show_guests_for_event_' in call.data:
            show_guests_for_event(call.message, int(call.data.split('_')[-1]))


@app.route('/', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    db = DbHelper()
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEB_HOOK_URL)
    app.run(host=APP_HOST, port=APP_PORT)
