from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
import datetime
from utils.get_city_user import city_info
from keyboards.keyboards import get_locations
from handlers.custom_handlers.history import command_history


@bot.message_handler(commands=['low', 'high', 'bestdeal', 'history'])
def commands(message: Message) -> None:
    command = message.text.strip('/')
    if command == 'history':
        bot.delete_state(message.from_user.id, message.chat.id)
        command_history(message)
    else:
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.set_state(message.from_user.id, UserInfoState.user_city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data.update({
                'user_id_telegram': message.from_user.id,
                'command': command,
                'location_id': None,
                'city': None,
                'adults': None,
                'children': None,
                'entry_date': None,
                'exit_date': None,
                'hotels_qty': None,
                'photos': None,
                'min_price': None,
                'max_price': None,
                'distance_from_center': None,
                'request_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            })
            bot.send_message(message.chat.id, "Введите город:")


@bot.message_handler(state=UserInfoState.user_city)
def get_user_city(message: Message) -> None:
    if message.text.isalpha():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
            locations = city_info(message.text)
            markup = get_locations(locations)
            bot.send_message(message.chat.id, 'Выберите локацию из списка:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод')