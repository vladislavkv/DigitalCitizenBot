import sqlite3
import telebot
import datetime
from re import *
from telebot import types

token='TOKEN'
bot=telebot.TeleBot(token)

conn=sqlite3.connect('usersDatabase.db')
cursor=conn.cursor()

user_data={'number':'','fullName':'','dob':'','email':''}

dob_pattern=compile('(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.]((19|20)\d\d)$')
email_pattern=compile('[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,}')
fullName_engPattern=compile('([A-z]{2,}) ([A-z]{2,})')
fullName_ruPattern=compile('([А-я]{2,}) ([А-я]{2,})')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Вас приветствует DigitalCitizenBot!\n'
                     'Здесь Вы сможете оставить жалобу или обращение по любому интересующему Вас вопросу.')
    check_number(message)

#  ------------------
# | Регистрация/вход |
#  ------------------

def check_number(message):
    keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
    checkPhone_button=types.KeyboardButton(text='Отправить номер телефона',request_contact=True)
    keyboard.add(checkPhone_button)
    bot.send_message(message.chat.id,'Пожалуйста, отправьте номер телефона, чтобы мы проверили Вашу регистрацию.',reply_markup=keyboard)
    bot.register_next_step_handler(message,check_reg)
    
def check_reg(message):
    if message.contact is None:
        check_number(message)
    else:
        user_data['number']=message.contact.phone_number
        conn=sqlite3.connect('usersDatabase.db')
        cursor=conn.cursor()
        result=cursor.execute('Select * from users where number="%s"'%(user_data['number'])).fetchone()
        if result is not None:
            main_menu(message)
        else:
            reg(message)

def reg(message):
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Упс, похоже что Вы не зарегестрированы.\n'
                     '\nНичего, сейчас я задам несколько простых вопросов, ответив на которые Вы сможете пользоваться сервисом.',reply_markup=keyboard)
    get_fullName(message)
        
def get_fullName(message):
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Введите полное имя и фамилию:',reply_markup=keyboard)
    bot.register_next_step_handler(message,reg_fullName)

def reg_fullName(message):
    user_data['fullName']=message.text.strip(' ').title()
    valid_fullName=fullName_engPattern.match(user_data['fullName']) or \
                    fullName_ruPattern.match(user_data['fullName'])
    if valid_fullName:
        get_dob(message)
    else:
        bot.send_message(message.chat.id,'Не правильные имя и фамилия, попробуйте еще раз.')
        get_fullName(message)

def get_dob(message):
    bot.send_message(message.chat.id,'Введите дату рождения в формате mm.dd.yyyy:')
    bot.register_next_step_handler(message,reg_dob)

def reg_dob(message):
    user_data['dob']=message.text
    valid_dob=dob_pattern.match(user_data['dob'])
    if valid_dob:
        get_email(message)
    else:
        bot.send_message(message.chat.id,'Не правильная дата рождения, попробуйте еще раз.')
        get_dob(message)

def get_email(message):
    bot.send_message(message.chat.id,'Введите e-mail для связи:')
    bot.register_next_step_handler(message,reg_email)

def reg_email(message):
    user_data['email']=message.text.replace(' ','').lower()
    valid_email=email_pattern.match(user_data['email'])
    if valid_email:
        check_data(message)
    else:
        bot.send_message(message.chat.id,'Не правильный e-mail, попробуйте еще раз.')
        get_email(message)

def check_data(message):
    keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_button=types.KeyboardButton('Подтвердить')
    again_button=types.KeyboardButton('Заново')
    keyboard.row(confirm_button,again_button)
    bot.send_message(message.chat.id,'Пожалуйста, проверьте еще раз и подтвердите введенные Вами данные:\n'
                     '\nНомер телефона: '+user_data['number']+'\n'
                     'Имя и фамилия: '+user_data['fullName']+'\n'
                     'Дата рождения: '+user_data['dob']+'\n'
                     'E-mail адрес: '+user_data['email'],reply_markup=keyboard)
    bot.register_next_step_handler(message,check_dataButton)

def check_dataButton(message):
    if message.text=='Подтвердить':
        save_data(message)
    elif message.text=='Заново':
        get_fullName(message)
    else:
        bot.send_message(message.chat.id,'Вы не нажали на кнопку.')
        check_data(message)

def save_data(message):
    conn=sqlite3.connect('usersDatabase.db')
    cursor=conn.cursor()
    cursor.execute('Insert into users values ("%s","%s","%s","%s")'% \
                   (user_data['number'],user_data['fullName'],user_data['dob'],user_data['email']))
    conn.commit()
    conn.close()
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Данные успешно сохранены.',reply_markup=keyboard)
    main_menu(message)

#  --------------
# | Главное меню |
#  --------------

def main_menu(message):
    keyboard=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    about_button=types.KeyboardButton('О проекте')
    sendMessage_button=types.KeyboardButton('Отправить обращение')
    myMessages_button=types.KeyboardButton('Мои обращения')
    feedback_button=types.KeyboardButton('Обратная связь')
    keyboard.add(sendMessage_button,myMessages_button)
    keyboard.row(about_button,feedback_button)
    bot.send_message(message.chat.id,'Выберите действие: ',reply_markup=keyboard)
    bot.register_next_step_handler(message,check_menuButton)

def check_menuButton(message):
    if message.text=='Отправить обращение':
       send_message(message)
    elif message.text=='Мои обращения':
        my_messages(message)
    elif message.text=='О проекте':
        about(message)
    elif message.text=='Обратная связь':
        feedback(message)

def category_sendMessage(message):
    keyboard=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    =types.KeyboardButton('О проекте')
    =types.KeyboardButton('О проекте')
    =types.KeyboardButton('О проекте')
    =types.KeyboardButton('О проекте')
    keyboard.add(sendMessage_button,myMessages_button)
    bot.send_message(message.chat.id,'Выберите категорию обращения:',reply_markup=keyboard)
    

bot.polling(none_stop=True)
