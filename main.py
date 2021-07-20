import gspread
import pandas as pd
import telebot
from datetime import datetime

bot = telebot.TeleBot("1827960987:AAFp54Ori1Y1_QjPpwsr56h8DXRk133VgPA")
admin_id = [678438649]
gc = gspread.service_account(filename='telebot-320415-75d8cf5bbe9c.json')
sh = gc.open("Bot")

# admin


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['start'])
def welcome_admin(message):
    bot.send_message(message.chat.id, "Привет, администратор.\n"
                                      "Введи /add, чтобы добавить новый реактив.\n"
                                      "Введи /change_amount, чтобы изменить количество реактива.\n"
                                      "Введи /change_name, чтобы изменить название реактива.\n"
                                      "Введи /delete, чтобы удалить реактив.\n"
                                      "Введи /take, чтобы взять реактив.")


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['add'])
def add(message):
    msg = bot.send_message(message.chat.id, 'Введи название реактива.')
    bot.register_next_step_handler(msg, add_name)


def add_name(message):
    try:
        name = message.text
        data = pd.read_csv('reactives.csv')
        if name not in data['reactive'].values:
            new_row = pd.DataFrame({'reactive': name, 'amount': 0}, index=[0])
            data = pd.concat([data, new_row]).reset_index(drop=True)
            data.to_csv('reactives.csv', index=False)
            worksheet = sh.add_worksheet(title=name, rows="100", cols="20")
            worksheet.update('T1', str(2))
            msg = bot.send_message(message.chat.id,
                                   'Введи текущее количество реактива. (Например, 4)')
            bot.register_next_step_handler(msg, add_amount, name)
        else:
            bot.send_message(message.chat.id,
                             'Такой реактив уже существует. Проверь название и начни с команды /start.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


def add_amount(message, name):
    try:
        amount = int(message.text)
        data = pd.read_csv('reactives.csv', index_col='reactive')
        data.loc[name]['amount'] = amount
        data.to_csv('reactives.csv')
        bot.send_message(message.chat.id,
                         'Реактив успешно добавлен.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['change_amount'])
def change_amount(message):
    msg = bot.send_message(message.chat.id, 'Введи название реактива.')
    bot.register_next_step_handler(msg, change_amount_name)


def change_amount_name(message):
    try:
        name = message.text
        data = pd.read_csv('reactives.csv')
        if name in data['reactive'].values:
            msg = bot.send_message(message.chat.id,
                                   'Введи новое количество реактива. (Например, 4)')
            bot.register_next_step_handler(msg, change_amount_amount, name)
        else:
            bot.send_message(message.chat.id, 'Такой реактив не существует. Проверь название и начни с команды /start.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


def change_amount_amount(message, name):
    try:
        amount = int(message.text)
        data = pd.read_csv('reactives.csv', index_col='reactive')
        data.loc[name]['amount'] = amount
        data.to_csv('reactives.csv')
        bot.send_message(message.chat.id,
                         'Количество реактива успешно обновлено.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['change_name'])
def change_name(message):
    msg = bot.send_message(message.chat.id, 'Введи старое название реактива.')
    bot.register_next_step_handler(msg, change_name_name)


def change_name_name(message):
    try:
        name = message.text
        data = pd.read_csv('reactives.csv')
        if name in data['reactive'].values:
            msg = bot.send_message(message.chat.id,
                                   'Введи новое название реактива.')
            bot.register_next_step_handler(msg, change_name_new_name, name)

        else:
            bot.send_message(message.chat.id, 'Такой реактив не существует. Проверь название и начни с команды /start.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


def change_name_new_name(message, name):
    try:
        new_name = message.text
        data = pd.read_csv('reactives.csv', index_col='reactive')
        data.rename(index={name: new_name}, inplace=True)
        data.to_csv('reactives.csv')
        sh.duplicate_sheet(source_sheet_id=sh.worksheet(name).id, new_sheet_name=new_name)
        sh.del_worksheet(sh.worksheet(name))
        bot.send_message(message.chat.id,
                         'Наименование реактива успешно обновлено.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['delete'])
def delete(message):
    msg = bot.send_message(message.chat.id, 'Введи название реактива для удаления.')
    bot.register_next_step_handler(msg, delete_name)


def delete_name(message):
    try:
        name = message.text
        data = pd.read_csv('reactives.csv', index_col='reactive')
        data = data.drop(index=[name])
        data.to_csv('reactives.csv')
        sh.del_worksheet(sh.worksheet(name))
        bot.send_message(message.chat.id,
                         'Реактив успешно удален.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


@bot.message_handler(func=lambda message: message.chat.id in admin_id, commands=['take'])
def take(message):
    msg = bot.send_message(message.chat.id, "Привет, какой реагент хочешь взять?")
    bot.register_next_step_handler(msg, take_name)


# Not admin


@bot.message_handler(commands=['start'])
def welcome(message):
    msg = bot.send_message(message.chat.id, "Привет, какой реагент хочешь взять?")
    bot.register_next_step_handler(msg, take_name)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Привет, всегда начинай работу с ботом с команды /start.")


@bot.message_handler(content_types=['text'])
def send_text(message):
    bot.send_message(message.chat.id, "Привет, начни с /start.")


def take_name(message):
    try:
        name = message.text
        data = pd.read_csv('reactives.csv', index_col='reactive')
        if name in data.index:
            amount = data.loc[name]['amount']
            msg = bot.send_message(message.chat.id,
                                   f'Сколько хочешь взять? Доступно {amount} единиц. (Например, 4)')
            bot.register_next_step_handler(msg, take_amount, name)
        else:
            bot.send_message(message.chat.id, 'Такого реактива нет. Проверь название, учитывая регистр,'
                                              ' и начни с команды /start.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


def take_amount(message, name):
    try:
        data = pd.read_csv('reactives.csv', index_col='reactive')
        if data.loc[name]['amount'] >= int(message.text) >= 0:
            data.loc[name]['amount'] -= int(message.text)
            data.to_csv('reactives.csv')
            worksheet = sh.worksheet(name)
            val = worksheet.acell('T1').value
            if val is None:
                val = 2
            val = int(val)
            worksheet.update(f'A{val}', str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            worksheet.update(f'B{val}', message.from_user.first_name + " " + message.from_user.last_name)
            worksheet.update(f'C{val}', str(int(message.text)))
            val += 1
            worksheet.update('T1', str(val))
            bot.send_message(message.chat.id, f'Ты взял {int(message.text)} единиц {name}.')
        else:
            bot.send_message(message.chat.id,
                             'Столько реактива нет, попробуй запросить меньше и начни с команды /start.')
    except Exception as e:
        bot.reply_to(message, 'Ошибка, начни с команды /start.')


bot.polling()
