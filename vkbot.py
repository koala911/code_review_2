import vk_api
import bs4
from vk_api.longpoll import VkLongPoll, VkEventType
import re
import requests

token = "ad717cbc60d260bf17875fa8b7e1c0656dbb34dac2bb5007c8367297a2e470010e8d26a01adf2f99e38a3"

vk = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk)

usersCity = dict()

class VkBot:

    def run(self):
        """
        Runs the bot
        """

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:

                    message = event.text.lower()

                    self.answer(message, event.user_id, event.random_id)

    def writeMessage(self, user_id, message, random_id):
        """
        Writes message to the user
        :param user_id: User's ID
        :param message: Text of message
        :param random_id: Random ID
        """
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id})

    def answer(self, message, user_id, random_id):
        """
        Answers on user's message
        :param message:
        :param user_id:
        :param random_id:
        :return:
        """

        myMessage = ''

        if (not user_id in usersCity):
            myMessage = "Введите свой город"
            usersCity[user_id] = -1

        elif (usersCity[user_id] == -1):
            try:

                self.getWeather(message)
                usersCity[user_id] = message
                myMessage = "Хорошо, теперь напиши 'help', чтобы узнать команды, которые я поддерживаю"

            except:

                myMessage = "Не нашел такого города.."

        elif (message == 'погода'):

            myMessage = self.getWeather(usersCity[user_id])

        elif (re.match('погода ', message) and not re.match('погода за месяц', message) and len(message) > 8):

            myMessage = self.getWeather(message[7].upper() + message[8:])

        elif (message == 'погода за месяц'):

            myMessage = usersCity[user_id][0].upper() + usersCity[user_id][1:] + ' за месяц'

        elif (re.match('погода за месяц ', message) and len(message) > 17):

            myMessage = message[16].upper() + message[17:] + ' за месяц'

        elif (message == 'help'):

            myMessage = "'Погода' - узнать погоду в твоем городе\n \
                        'Погода название_города' - погода в этом городе\n \
                        'Погода за месяц' - график температуры за последние 30 дней\n \
                        'Погода за месяц название_города' - график температуры за последние 30 дней в этом городе"
        else:

            myMessage = "Не понял тебя.."

        self.writeMessage(user_id, myMessage, random_id)

    def getWeather(self, city = "москва"):
        """
        Gets the weather
        :param city: city, in which we get the weather
        :return:
        """
        request = requests.get("https://sinoptik.com.ru/погода-" + city)
        b = bs4.BeautifulSoup(request.text, "html.parser")

        try:
            p3 = b.select('.temperature .p3')
            weather1 = p3[0].getText()

            p4 = b.select('.temperature .p4')
            weather2 = p4[0].getText()

            p5 = b.select('.temperature .p5')
            weather3 = p5[0].getText()

            p6 = b.select('.temperature .p6')
            weather4 = p6[0].getText()

            result = ''
            result = result + ('Утром :' + weather1 + ' ' + weather2) + '\n'
            result = result + ('Днём :' + weather3 + ' ' + weather4) + '\n'
            temp = b.select('.rSide .description')
            weather = temp[0].getText()
            result = result + weather.strip()

            return result

        except:
            
            return "Не нашел такого города.."