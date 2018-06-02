import sqlite3
import telebot
import datetime
from re import *
from telebot import types

token=''
bot=telebot.TeleBot(token)

conn=sqlite3.connect('usersDatabase.db')
cursor=conn.cursor()

user_data={'number':'','fullName':'','dob':'','email':''}

email_pattern=compile('[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,}')

method=('Имя и фамилия','Дата рождения','E-mail')
suffix=('ые ','ая ','ый ')


def error(message):
    bot.send_message(message.chat.id,'Не правильн'+suffix[suf_ind]+method[meth_ind]+', попробуйте еще раз.')
    if step == 1:
        get_fullName(message)
    elif step == 2:
        get_dob(message)
    else step == 3:
        get_email(message)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Вас приветствует DigitalCitizenBot!\n'
                     'Здесь Вы сможете оставить жалобу или обращение по любому интересующему Вас вопросу.')
    check_number(message)

def check_number(message):
    keyboard=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
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
            bot.send_message(message.chat.id,'vy zaregany')
        else:
            reg(message)

def reg(message):
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Упс, похоже что Вы не зарегестрированы.\n'
                     '\nНичего, сейчас я задам несколько простых вопросов, ответив на которые Вы сможете пользоваться сервисом.',reply_markup=keyboard)
    get_fullName(message)
        
def get_fullName(message):
    global step,suf_ind,meth_ind
    step=1
    suf_ind=0
    meth_ind=0
    bot.send_message(message.chat.id,'Введите полное имя и фамилию:')
    bot.register_next_step_handler(message,reg_fullName)

def reg_fullName(message):
    user_data['fullName']=message.text
    get_dob(message)
def get_dob(message):
    step=2
    suf_ind=1
    meth_ind=1
    bot.send_message(message.chat.id,'Введите дату рождения:')
    bot.register_next_step_handler(message,reg_dob)

def reg_dob(message):
    user_data['dob']=message.text
    get_email(message)
def get_email(message):
    step=3
    suf_ind=2
    meth_ind=2
    bot.send_message(message.chat.id,'Введите e-mail для связи:')
    bot.register_next_step_handler(message,reg_email)

def reg_email(message):
    user_data['email']=message.text.replace(' ','').lower()
    check_data(message)
def check_data(message):
    valid_email=email_pattern.match(user_data['email'])
    if valid_email:
        keyboard=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
        confirm_button=types.KeyboardButton('Подтвердить')
        again_button=types.KeyboardButton('Заново')
        keyboard.row(confirm_button,again_button)
        bot.send_message(message.chat.id,'Пожалуйста, проверьте еще раз и подтвердите введенные Вами данные:\n'
                         '\nНомер телефона: '+user_data['number']+'\n'
                         'Имя и фамилия: '+user_data['fullName']+'\n'
                         'Дата рождения: '+user_data['dob']+'\n'
                         'E-mail адрес: '+user_data['email'],reply_markup=keyboard)
    else:
        error(message)

    #cursor.execute('Insert into users values ("%s","%s","%s","%s")'% \
    #               (user_data['number'],user_data['fullName'],user_data['dob'],user_data['email']))
    #conn.commit()
#conn.close()
bot.polling(none_stop=True)
