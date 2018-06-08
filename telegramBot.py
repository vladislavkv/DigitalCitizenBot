import sqlite3
import telebot
import datetime
from re import *
from messages import *
from telebot import types
from telegram import ParseMode #pip install python-telegram-bot --upgrade

token='592422673:AAHQjN-JyevhnnkrAZ01fvyIwlDuic50PXU'
bot=telebot.TeleBot(token)

conn=sqlite3.connect('usersDatabase.db')
conn=sqlite3.connect('messages.db')
cursor=conn.cursor()

send_message={'category':'','address':'','text':''}
user_data={'number':'','fullName':'','dob':'','email':''}

category_pattern=compile('^[А-я ]{2,30}$')
text_pattern=compile('^[0-9A-zА-я-.,/ \"]{20,1000}$')
address_pattern=compile('^[0-9A-zА-я-.,/ \"]{5,50}$')
dob_pattern=compile('(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.]((19|20)\d\d)$')
email_pattern=compile('[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,}')
fullName_engPattern=compile('([A-z]{2,}) ([A-z]{2,})')
fullName_ruPattern=compile('([А-я]{2,}) ([А-я]{2,})')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Вас приветствует <b>DigitalCitizenBot!</b>\n' \
                     'Здесь Вы сможете оставить жалобу или обращение по любому интересующему Вас вопросу.',parse_mode=ParseMode.HTML)
    check_number(message)

#  ------
# | Вход |
#  ------

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
            bot.send_message(message.chat.id,'Все чисто, проходите.')
            main_menu(message)
        else:
            reg(message)

#  -------------
# | Регистрация |
#  -------------

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
    confirmButton=types.KeyboardButton('Подтвердить')
    againButton=types.KeyboardButton('Заново')
    keyboard.row(confirmButton,againButton)
    bot.send_message(message.chat.id,'Пожалуйста, проверьте еще раз и подтвердите введенные Вами данные:\n'
                     '\nНомер телефона:\n'+user_data['number']+'\n'
                     'Имя и фамилия:\n'+user_data['fullName']+'\n'
                     'Дата рождения:\n'+user_data['dob']+'\n'
                     'E-mail адрес:\n'+user_data['email'],reply_markup=keyboard)
    bot.register_next_step_handler(message,check_dataButtons)

def check_dataButtons(message):
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
    bot.register_next_step_handler(message,check_menuButtons)

def check_menuButtons(message):
    if message.text=='Отправить обращение':
       get_categories(message)
    elif message.text=='Мои обращения':
        get_myMessages(message)
    elif message.text=='О проекте':
        about_project(message)
    elif message.text=='Обратная связь':
        feedback(message)
    else:
        bot.send_message(message.chat.id,'Кажется, что у меня нет такой кнопки, выберите существующую.')
        main_menu(message)

#  --------------------
# | Отправка обращения |
#  --------------------

def get_categories(message):
    keyboard=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    category1Button=types.KeyboardButton('Грязь и мусор')
    category2Button=types.KeyboardButton('Ямы')
    category3Button=types.KeyboardButton('Неисправное освещение')
    allCategoriesButton=types.KeyboardButton('Показать все категории')
    editFavoriteCategoriesButton=types.KeyboardButton('Изменить избранные категории')
    mainMenuButton=types.KeyboardButton('Вернуться в меню')
    addCategoryButton=types.KeyboardButton('Своя категория')
    keyboard.add(category1Button,category2Button,category3Button,allCategoriesButton, \
                 editFavoriteCategoriesButton,addCategoryButton,mainMenuButton)
    bot.send_message(message.chat.id,'Выберите категорию обращения:',reply_markup=keyboard)
    bot.register_next_step_handler(message,reg_categories)
    
def reg_categories(message):
    if message.text=='Грязь и мусор':
        send_message['category']=message.text
        get_address(message)
    elif message.text=='Ямы':
        send_message['category']=message.text
        get_address(message)
    elif message.text=='Неисправное освещение':
        send_message['category']=message.text
        get_address(message)
    elif message.text=='Своя категория':
        get_newCategory(message)
    elif message.text=='Показать все категории' or 'Изменить избранные категории':
        bot.send_message(message.chat.id,'Такой команды пока-что нет')
        get_categories(message)
    else:
        bot.send_message(message.chat.id,'Я не знаю такой категории, выберите из существующих.')
        get_categories(message)

def get_newCategory(message):
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Введите название категории:',reply_markup=keyboard)
    bot.register_next_step_handler(message,reg_newCategory)

def reg_newCategory(message):
    send_message['category']=message.text
    valid_category=category_pattern.match(send_message['category'])
    if valid_category:
        get_address(message)
    else:
        bot.send_message(message.chat.id,'Разрешены только буквеные символы. Длина категории должна соответствовать 2-30 символам.')
        get_newCategory(message)

def get_address(message):
    keyboard=types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,'Введите тот адрес, где Вы впервые увидели это недоразумение:',reply_markup=keyboard)
    bot.register_next_step_handler(message,reg_address)

def reg_address(message):
    send_message['address']=message.text
    valid_address=address_pattern.match(send_message['address'])
    if valid_address:
        get_text(message)
    else:
        bot.send_message(message.chat.id,'Разрешены только символы (-.,/"). Длина адреса должна соответствовать 5-50 символам.')
        get_address(message)

def get_text(message):
    bot.send_message(message.chat.id,'Опишите возникшую проблему:')
    bot.register_next_step_handler(message,reg_text)

def reg_text(message):
    send_message['text']=message.text
    valid_text=text_pattern.match(send_message['text'])
    if valid_text:
        save_message(message)
    else:
        bot.send_message(message.chat.id,'Разрешены только символы (-.,/"). Длина сообщения должна соответствовать 20-1000 символам.')
        get_text(message)

def save_message(message):
    conn=sqlite3.connect('messages.db')
    cursor=conn.cursor()
    cursor.execute('Insert into messages values ("%s","%s","%s","%s","На рассмотрении")'% \
                   (send_message['category'],send_message['address'],send_message['text'],user_data['number']))
    conn.commit()
    bot.send_message(message.chat.id,'Спасибо! Ваше обращение передано на рассмотрение.')
    send_messageAgain(message)

def send_messageAgain(message):
    keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
    mainMenuButton=types.KeyboardButton('Меню')
    againButton=types.KeyboardButton('Заново')
    keyboard.row(mainMenuButton,againButton)
    bot.send_message(message.chat.id,'Желаете написать еще одно обращение?',reply_markup=keyboard)
    bot.register_next_step_handler(message,check_messageButtons)

def check_messageButtons(message):
    if message.text=='Меню':
        main_menu(message)
    elif message.text=='Заново':
        get_categories(message)
    else:
        bot.send_message(message.chat.id,'Вы не нажали на кнопку.')
        send_messageAgain(message)

#  ---------------
# | Мои обращения |
#  ---------------

def get_myMessages(message):
    number=0
    conn=sqlite3.connect('messages.db')
    cursor=conn.cursor()
    result=cursor.execute('Select * from messages where number = "%s"'%(user_data['number']))
    results=cursor.fetchall()
    number=0
    if result is not None:
        for result in results:
            number=number+1
            bot.send_message(message.chat.id,'<b>Номер: %s</b>\n\nКатегория:\n%s\n\nАдрес:\n%s\n\nТекст обращения:\n%s\n\nСтатус:\n%s' \
                             %(number,result[0],result[1],result[2],result[4]),parse_mode=ParseMode.HTML)
        main_menu(message)
    else:
        bot.send_message(message.chat.id,'Здесь пока-что пусто.')
        main_menu(message)

#  -----------
# | О проекте |
#  -----------

def about_project(message):
    bot.send_message(message.chat.id,'Клуб активистов города, которым не все равно, где жить...'
                     '<a href="http://telegra.ph/O-PROEKTE-06-07">Читать далее</a>',parse_mode=ParseMode.HTML)
    main_menu(message)

#  ----------------
# | Обратная связь |
#  ----------------

def feedback(message):
    bot.send_message(message.chat.id,'<a href="https://telegram.org">Ссылка на сайт</a>',parse_mode=ParseMode.HTML)
    main_menu(message)

conn.close()
bot.polling(none_stop=True)
