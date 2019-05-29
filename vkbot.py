import vk_api
import bs4
from vk_api.longpoll import VkLongPoll, VkEventType
import re
import requests
import datetime
import matplotlib
import matplotlib.pyplot as plt

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

        elif (re.match('погода ', message) and not re.match('погода на неделю', message) and len(message) > 8):

            myMessage = self.getWeather(message[7].upper() + message[8:])

        elif (message == 'погода на неделю'):

            forecast = self.getForecast(usersCity[user_id])

            for date in forecast:

                myMessage += date
                myMessage += ': '

                if (forecast[date] > 0):
                    myMessage += '+'

                elif (forecast[date] < 0):
                    myMessage += '-'

                myMessage += str(forecast[date])
                myMessage += '°\n'

        elif (re.match('погода на неделю ', message) and len(message) > 18):

            forecast = self.getForecast(message[16:])

            if (isinstance(forecast, dict)):

                for date in forecast:

                    myMessage += date
                    myMessage += ': '

                    if (forecast[date] > 0):
                        myMessage += '+'

                    elif (forecast[date] < 0):
                        myMessage += '-'

                    myMessage += str(forecast[date])
                    myMessage += '°\n'

            else:

                myMessage = "Не нашел такого города.."

        elif (message == 'help'):

            myMessage = "'Погода' - узнать погоду в твоем городе\n \
                        'Погода название_города' - погода в этом городе\n \
                        'Погода на неделю - прогноз погоды на неделю\n \
                        'Погода на неделю название_города' - пргоноз погоды на неделю в этом городе"
        else:

            myMessage = "Не понял тебя.."

        self.writeMessage(user_id, myMessage, random_id)

    def getWeather(self, city = "москва"):
        """
        Gets the weather
        :param city: city, in which we get the weather
        :return: weather
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

    def getForecast(self, city = 'Москва'):
        """
        Gets the forecast on week
        :param city: city, in which we get the forecast
        :return: forecast
        """

        try:

            result = {}
            currentDate = datetime.datetime.today().date()

            for i in range(7):

                request = requests.get("https://sinoptik.com.ru/погода-" + city + '#' + str(currentDate + datetime.timedelta(days=i)))
                b = bs4.BeautifulSoup(request.text, "html.parser")

                p5 = b.select('.temperature .p5')
                weather = p5[0].getText()
                weather = weather[:(len(weather) - 1)]

                result[str(currentDate + datetime.timedelta(days=i))] = int(weather)

                print(int(weather))

            return result

        except:

            return "Не нашел такого города.."

    def drawForecast(self, forecast):

        fig = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
        ax = fig.add_axes([0, 0, 1, 1])
        plt.grid(True)
        plt.xlabel('Date')
        plt.ylabel('Temperature')
        x = forecast.keys()
        y = forecast.values()
        plt.plot(x, y, label='1', color='red', linewidth=2)
        #ax.legend()
        plt.interactive(True)
        plt.show(block=True)

        plt.savefig('myGraf.png')
