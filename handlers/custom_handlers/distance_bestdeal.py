from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
from utils.hotels_params import get_data
from utils.hotel_information import hotel_info
from database.models import History


@bot.message_handler(state=UserInfoState.distance)
def distance_from_center(message: Message):
    try:
        distance_km = float(message.text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['center_distance'] = distance_km

        bot.send_message(message.chat.id, 'Расстояние от центра записано. Ждите результаты...')
        filters = {
            "price": {
                "max": data.get('price_max_bestdeal'),
                "min": data.get('price_min_bestdeal')
            }
        }
        try:
            result, hotel_ids = get_data(data, sort_type="DISTANCE", filters=filters)
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка при получении данных отеля: {str(e)}')
            return

        if result and hotel_ids:
            bot.send_message(message.chat.id, result)
            for hotel_id in hotel_ids:
                hotel_data = {"property_id": hotel_id, "photos": data.get('photos')}
                try:
                    hotel_info_result = hotel_info(hotel_data)
                except Exception as e:
                    bot.send_message(message.chat.id, f'Ошибка при получении информации об отеле: {str(e)}')
                    continue

                if hotel_info_result:
                    hotel_info_str, photo_urls = hotel_info_result
                    bot.send_message(message.chat.id, hotel_info_str)
                    if photo_urls:
                        for photo_url in photo_urls:
                            bot.send_photo(message.chat.id, photo_url)
                else:
                    bot.send_message(message.chat.id, 'Нет информации об этом отеле.')
        else:
            bot.send_message(message.chat.id, 'Нет доступных отелей по вашему запросу.')


        if data.get("command") in ['bestdeal']:
            History.create(
                user_id=message.from_user.id,
                command=data.get('command'),
                city=data.get('city'),
                location_id=data.get('id_location'),
                adults_qty=data.get('adults'),
                children=data.get('child_amount', 0),
                entry_date=data.get('entry'),
                exit_date=data.get('exit'),
                hotels_quantity=data.get('hotels_qty'),
                photo_qty=data.get('photos', 0),
                min_price=data.get('price_min_bestdeal', 0),
                max_price=data.get('price_max_bestdeal', 0),
                distance_from_center=data.get('center_distance', 0),
                request_date=data.get('request_date')
            )
        bot.delete_state(message.from_user.id, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректное значение, пожалуйста введите число.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')
