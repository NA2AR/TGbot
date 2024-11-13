import telebot
import random
from telebot import types
from telebot.handler_backends import State, StatesGroup
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from ClasBase import create_table, Student, Words, StudentWords

Token = '7459851398:AAGz8T8hc8KLKl12KdQ0mlw_DBsJPNknYRw'
DSN = 'postgresql://postgres:rfhfrfnbwf1975@localhost:5432/test_db'
engine = sqlalchemy.create_engine(DSN)
bot = telebot.TeleBot(Token)

create_table(engine)

Session = sessionmaker(bind=engine)
session = Session() 

words_1 = Words(words='land', translate='земля')
words_2 = Words(words='picture', translate='картина')
words_3 = Words(words='animal', translate='животное')
words_4 = Words(words='peace', translate='мир')

session.add_all([words_1, words_2, words_3, words_4])
session.commit()

translate_w = []
target_w = []

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    start_bot(message)

@bot.message_handler(commands=['cards', 'start'])
def start_bot(message):
    del target_w[0::1]
    chat_id = message.from_user.id
    if not session.query(Student.name).filter(Student.name.like(f'%%{chat_id}%%')).all():
        s = Student(name=f'{chat_id}')
        session.add(s)
        session.commit()
        sw_1 = StudentWords(words_id= words_1.id,Student_id= s.id)
        sw_2 = StudentWords(words_id= words_2.id,Student_id= s.id)
        sw_3 = StudentWords(words_id= words_3.id,Student_id= s.id)
        sw_4 = StudentWords(words_id= words_4.id,Student_id= s.id)
        session.add_all([sw_1,sw_2,sw_3,sw_4])
        session.commit()
        session.close()

    for w in session.query(Words).all():
        target_w.append(w.words)
    random.shuffle(target_w)
    for w in session.query(Words).filter(Words.words.like(target_w[0])).all():
        translate_w = (w.translate)
        
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = target_w[0:4]
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])
    markup.add(*buttons)
    bot.send_message(message.chat.id, f'Угадай слово {translate_w}', reply_markup= markup)
    
    print(target_w)
    
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_w[0]
        data['translate_word'] = translate_w
        data['other_words'] = target_w[1::1]
        
@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    new_word = Words(words=words, translate=translate)
    session.add(new_word)
    session.commit()
    session.close()

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    session.query(Words).filter(Words.words == f'{message}').delete()
    session.commit()
    session.close()
    start_bot(message)

@bot.message_handler(func=lambda message: True, content_types=['text']) 
def message_reply(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
    if message.text == target_word:
        bot.send_message(message.chat.id, 'Все правильно')
        start_bot(message)
    else:
        bot.send_message(message.chat.id, 'Не правильно')
    print(target_w)    

if __name__ == '__main__':
    print('Bot running!')
    bot.polling()