from pyrogram import Client, filters, emoji
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove
from data import constellations, north_hemisphere
from random import choice


mode = 'general'
image_caption = "Сузір'я {} - {}"
score = 0


def is_mode(mode_name):
    """Custom filter."""
    return filters.create(lambda flt, __, query: mode == flt.data, data=mode_name)


app = Client("my_bot")


@app.on_message(filters.command(['start']))
def bot_start(client, message: Message):
    greeting = "Вітаю, я Stelliria! Допоможу вам поринути в чарівний світ сузір'їв! " \
              "Напишіть назву або виберіть з режимів нижче..."
    app.send_message(message.chat.id, greeting, reply_markup=ReplyKeyboardMarkup(
       [["Знайти за назвою", f"Випадкове сузір'я {emoji.GAME_DIE}"],
        [f"Зіграти в гру {emoji.SOCCER_BALL}", 'Список сузір\'їв'], ["About"]], resize_keyboard=True))


def random_constellation():
    """Pick random a key from constellations dict."""
    return choice(list(constellations.keys()))


def prettify_name(raw_name):
    """Capitalize each word of the name."""
    raw_name = raw_name.replace('_', ' ')
    return ' '.join(map(lambda n: n.capitalize(), raw_name.split()))


def check_name(name):
    """Check whether name is the name of existing constellation."""
    name = prettify_name(name)
    return True if name in constellations else False


def play_game(chat_id):
    """Send random constellation with inline buttons."""
    name = choice(north_hemisphere)
    in_latin = prettify_name(constellations[name])
    app.send_photo(chat_id, f'gallery/{constellations[name]}.jpg',
                   caption=image_caption.format(name, in_latin), reply_markup=InlineKeyboardMarkup([
              [InlineKeyboardButton('Знайшов', callback_data='next_game'),
               InlineKeyboardButton('Пропустити', callback_data='skip_game')],
              [InlineKeyboardButton('Закінчити гру', callback_data='stop_game')]
            ]))


@app.on_message(filters.regex(f"Випадкове сузір'я {emoji.GAME_DIE}") & is_mode('general'))
def handle(client, message: Message):
    random_name = random_constellation()
    in_latin = prettify_name(constellations[random_name])
    app.send_photo(message.chat.id, f'gallery/{constellations[random_name]}.jpg',
                   caption=image_caption.format(random_name, in_latin), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Ще одне', callback_data='get_random_constellation')]
        ]))

# !!! Потім доробити перегляд інформації про сузір'я

#@app.on_message(filters.regex("Про сузір\'я") & is_mode('general'))
#def handle(client, message: Message):
#    global mode
#    mode = 'about'
#    app.send_message(message.chat.id, 'Про яке сузір\'я ви хочете почитати?')


#@app.on_message(filters.text & is_mode('about'))
#def handle(client, message: Message):
#    global mode
#    mode = 'general'
#
#    name = prettify_name(message.text)
#    if check_name(name):
#        app.send_message(message.chat.id, f'Сузір\'я {message.text} походить...')
#    else:
#        app.send_message(message.chat.id, 'Вибачте, я не можу знайти такого сузір\'я. Можливо неправильна назва')
#        app.send_message(message.chat.id, f'Спробуйте ще {emoji.SMILING_FACE}')


@app.on_message(filters.regex("About") & is_mode('general'))
def handle(client, message: Message):
    app.send_message(message.chat.id, 'Подяка naturenoon.com за картинки сузір\'їв.\n\nБот створений для швидкого '
                                'пошуку схемок сузір\'їв для тих, хто хоче навчитися знаходити їх на зоряному небі.\n\n'
                                      'Примітка: під час гри випадають лише сузір\'я північної півкулі.')

@app.on_message(filters.regex("Список сузір'їв") & is_mode('general'))
def handle(client, message: Message):
    cl = ''
    number = 1
    for name in list(constellations.keys()):
        if name not in ['Близнюки', 'Великий Віз', 'Малий Віз']:
            cl += f'{number}. {name}' + '\n'
            number += 1
    app.send_message(message.chat.id, cl[:-1])


@app.on_message(filters.regex(f"Зіграти в гру {emoji.SOCCER_BALL}") & is_mode('general'))
def handle(client, message: Message):
    app.send_message(message.chat.id, 'Як грати: вийдіть в зоряну безхмарну ніч надвір, та спробуйте відшукати на '
                                      'небі загадане сузір\'я', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton('Грати', callback_data='start_game')]
    ]))


@app.on_message(filters.regex("Знайти за назвою") & is_mode('general'))
def handle(client, message: Message):
    app.send_message(message.chat.id, 'Напишіть назву сузір\'я, яке ви хочете знайти')


@app.on_message(filters.text & is_mode('general'))
def handle(client, message: Message):
    name = prettify_name(message.text)

    if check_name(name):
        in_latin = prettify_name(constellations[name])
        app.send_photo(message.chat.id, f'gallery/{constellations[name]}.jpg',
                       caption=image_caption.format(name, in_latin))
    else:
        app.send_message(message.chat.id, 'Вибачте, я не можу знайти такого сузір\'я. Можливо неправильна назва')
        app.send_message(message.chat.id, f'Спробуйте ще {emoji.SMILING_FACE}')


@app.on_callback_query(filters.regex('get_random_constellation'))
def answer(client, query: CallbackQuery):
    random_name = random_constellation()
    in_latin = prettify_name(constellations[random_name])
    app.send_photo(query.message.chat.id, f'gallery/{constellations[random_name]}.jpg',
                   caption=image_caption.format(random_name, in_latin), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f'Ще одне {emoji.GAME_DIE}', callback_data='get_random_constellation')]
        ]))


@app.on_callback_query(filters.regex('start_game'))
def answer(client, query: CallbackQuery):
    play_game(query.message.chat.id)


@app.on_callback_query(filters.regex('next_game'))
def answer(client, query: CallbackQuery):
    global score
    query.answer('Молодець!')
    play_game(query.message.chat.id)
    query.message.delete()
    score += 1


@app.on_callback_query(filters.regex('skip_game'))
def answer(client, query: CallbackQuery):
    query.answer('Нічого, наступного разу!')
    play_game(query.message.chat.id)
    query.message.delete()


@app.on_callback_query(filters.regex('stop_game'))
def answer(client, query: CallbackQuery):
    global score
    if score == 0:
        result = 'Оу, на жаль ви не знайшли жодного сузір\'я. Але нічого, наступного разу пощастить!'
    else:

        result = 'Вуху! Чудова гра! Ви знайшли ' + str(score) + (" сузір\'я." if 1 <= score % 10 <= 4 else " сузір\'їв.")
    app.send_message(query.message.chat.id, result)
    score = 0


app.run()
