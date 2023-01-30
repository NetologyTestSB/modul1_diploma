import requests
from pprint import pprint
import time
from datetime import datetime
import json

# ╬ ═ ═ ╬ ╔ ╗ ╚ ╝ ╔ ═ ══ ╗ ║ ╚ ═ ══ ╝
def print_title(title):
    len_title = len(title) + 2
    print('╔', '═' * len_title, '╗', sep='')
    print('║', title, '║')
    print('╚', '═' * len_title, '╝', sep='')


def print_info(txt):
    print('*** INFO: ' + txt)

class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.photo_lst = []
        self.user_data = {}
        self.user_id = 780123654
        self.photo_qty = 0
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_name_surname(self, user_id):
        base_params = {
            'fields': 'photo_100'
        }
        req = requests.get(self.url + 'users.get', params={**self.params, **base_params, 'user_id': user_id}).json()
        self.user_data['name'] = req['response'][0]['first_name']
        self.user_data['surname'] = req['response'][0]['last_name']

    def get_photos(self, user_id=780123654, without_print=True) -> bool:
        '''  получение списка фото из профиля по номеру пользователя vk  '''
        photo_params = {
            'album_id': 'profile',
            'photo_sizes': 0,
            'rev': 1,
            'extended': 1
        }
        photo_url = 'photos.get'
        # чтобы при повторном вызове функции не оставались старые ссылки
        self.photo_lst = []
        res = requests.get(self.url + photo_url, params={**self.params, **photo_params, 'owner_id': user_id}).json()
        if 'error' in res.keys():
            print(res['error']['error_msg'])
            return
        lst = res['response']['items']
        self.photo_qty = len(lst)
        self.get_name_surname(user_id)
        print_title(f'Список фото из профиля пользователя: {self.user_data["name"]} {self.user_data["surname"]}   всего: {len(lst)}')
        for el in lst:
            self.photo_lst.append({'id': el['id'], 'date': el['date'], 'likes': el['likes']['count'], 'url': el['sizes'][-1]['url']})
            if not without_print:
                print(f'фото: {el["id"]}   дата: {datetime.fromtimestamp(el["date"]).strftime("%d.%m.%Y %H:%M:%S")}'
                      f'   макс. размер: {str(el["sizes"][-1]["width"]).rjust(5)} x {str(el["sizes"][-1]["height"]).ljust(5)}'
                      f'   кол-во лайков: {el["likes"]["count"]}')
        return True

    def save_photos_on_yandex(self, folder, photo_qty=5) -> bool:
        ''' загрузка файлов из списка self.photo_lst в папку на яндекс.диске
        :param folder: папка на яндекс.диске
        :return: True/False
        '''
        if len(self.photo_lst) == 0:
            return
        error = False
        # url яндекс.диска !!!
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        print_title(f'Выполняется запись файлов в папку {folder} на Яндекс.Диске')
        qty = len(self.photo_lst)
        for num, el in enumerate(self.photo_lst, 1):
            link = el['url']
            try:
                filename = str(el['likes']) + '.jpg'
                # авторизация на я.диске по токену в headers
                headers = ya.get_headers()
                # параметры пути на я.диске и url фото из интернета
                params = {
                    'path': folder + filename,
                    'url': link
                }
                res = requests.post(upload_url, headers=headers, params=params)
                res.raise_for_status()
                if res.status_code == 202:
                     fill = round(20 * num / photo_qty)
                     print(f'\r  {(100 * num / photo_qty):3.0f}% {("▒" * fill).ljust(20)} записывается файл: {filename}', end='')
                if num == photo_qty:
                    break
            except Exception as err:
                print(err)
                error = True
        if not error:
            print(f'\nЗапись успешно завершена, записано файлов: {photo_qty}')
            return True

class YandexDisk:
    def __init__(self, token):
        self.token = token_yandex

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_files_list(self):
        ''' получение плоского (из всех папок) списка всех файлов с яндекс.диска '''
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        headers = self.get_headers()
        response = requests.get(files_url, headers=headers, params={'limit': 100})
        dct = response.json()
        return dct

    def check_and_create_new_folder(self, folder_name, show_message=True) -> bool:
        ''' создание новой папки на яндекс.диске, если такой папки еще нет '''
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        try:
            response = requests.put(files_url, headers=headers, params={'path': folder_name})
            response.raise_for_status()
            if response.status_code == 201 and show_message:
                print_info(f'Папка {folder_name} успешно создана')
            return True
        except Exception as err:
            if response.status_code == 409:
                if show_message:
                    print_info(f'Папка {folder_name} уже существует')
            else:
                print_info(f'При создании папки возникла ошибка:\n{err}')


class UserOperations():
    ''' все операции для главного меню программы '''
    def __init__(self):
        self.user_id = 780123654 # мой номер акаунта
        self.folder_name = '/test_photo_from_vk/'
        self.photo_qty = 5

    def get_user_id(self) -> bool:
        ''' получение номера акаунта пользователя вк '''
        self.user_id = 780123654 # мой номер акаунта
        print('Введите id пользователя: ', end='')
        try:
            st = input()
            if st:
                self.user_id = int(st)
            return True
        except Exception as err:
            print_info('Номер пользователя должен быть натуральным числом')

    def get_and_check_yandex_token(self):
        ''' получение и проверка токена для авторизации на я.диске '''
        ya.token = input('Введите токен: ')
        try:
            token_url = 'https://cloud-api.yandex.net/v1/disk'
            headers = ya.get_headers()
            response = requests.get(token_url, headers=headers)
            response.raise_for_status()
            dct = response.json()
            print_info(f'Получен доступ к я.диску пользователя {dct["user"]["display_name"]}')
        except Exception as err:
            print(f'Ошибка доступа к Яндекс.Диску:\n{err}')



    def upload_photos_on_yandex(self):
        ''' загрузка фото на яндекс.диск '''
        if self.get_user_id():
            if vk_client.get_photos(self.user_id, without_print=True):
                if self.create_new_folder_on_yandex():
                    if self.select_photos_quantity():
                        vk_client.save_photos_on_yandex(self.folder_name, photo_qty=self.photo_qty)

    def get_photos_from_vk_profile(self):
        ''' просмотр списка фото по номеру пользователя вк '''
        if self.get_user_id():
            vk_client.get_photos(self.user_id, without_print=False)

    def create_new_folder_on_yandex(self) -> bool:
        ''' создание папки на яндекс.диске '''
        self.folder_name = '/test_photo_from_vk/'
        print('Введите имя новой папки (по умолчанию - test_photo_from_vk): ', end='')
        inp = input()
        if inp:
            self.folder_name = '/' + inp + '/'
        if ya.check_and_create_new_folder(self.folder_name):
            return  True

    def select_photos_quantity(self):
        ''' задание кол-ва загружаемх фото '''
        self.photo_qty = 5
        print(f'Введите количество загружаемых фото (всего имеется: {vk_client.photo_qty}): ', end='')
        try:
            st = input()
            if st:
                self.photo_qty = int(st)
            return True
        except Exception as err:
            print_info('Количество фото должно быть натуральным числом')

    def create_photo_list_file(self):
        ''' создание файла в компьютере со списком фото, загруженных на яндекс.диск '''
        json_dict = {}
        vk_client.get_name_surname(self.user_id)
        json_dict['id vk'] = self.user_id
        json_dict['name'] = vk_client.user_data['name']
        json_dict['surname'] = vk_client.user_data['surname']
        json_dict['dir yandex'] = 'disk:' + self.folder_name
        json_dict.setdefault('photos', [])
        # получаем плоский список файлов (все файлы)
        files_dict = ya.get_files_list()
        for dct in files_dict['items']:
            if self.folder_name in dct['path']:
                pdict = {}
                pdict['file_name'] = dct['path'].split('/')[-1]
                pdict['size'] = dct['size']
                json_dict['photos'].append(pdict)
        try:
            with open('yandex_photo_list.json', 'w', encoding='utf-8') as file:
                json.dump(json_dict['photos'], file, indent=3, ensure_ascii=False)
            print_info('Создан файл yandex_photo_list.json.')
        except Exception as err:
            print(err)

    def all_operations_sequence(self):
        ''' последовательное выполнение всех операций: номер-список фото-папка на я.д-загрузка фото на я.д-файл со списком'''
        if self.get_user_id():
            if vk_client.get_photos(self.user_id, without_print=True):
                if self.create_new_folder_on_yandex():
                    if self.select_photos_quantity():
                        if vk_client.save_photos_on_yandex(self.folder_name, photo_qty=self.photo_qty):
                            # иногда не успевает выполниться предыдущий запрос
                            time.sleep(1)
                            self.create_photo_list_file()

    def react_on_kbd(self):
        func_dict = {
            '1': self.get_photos_from_vk_profile,
            '2': self.get_and_check_yandex_token,
            '3': self.create_new_folder_on_yandex,
            '4': self.upload_photos_on_yandex,
            '5': self.all_operations_sequence
        }
        command = 'x'
        while command != '0':
            line = '═' * 65
            print(line, '\n',
                  f'0 - выход из программы\n'
                  f'1 - просмотреть таблицу имеющихся фото в профиле пользователя vk\n'
                  f'2 - ввести и проверить токен для авторизации на Яндекс.Диск\n'
                  f'3 - создать новую папку для записи файлов на Яндекс.Диск\n'
                  f'4 - записать фото на Яндекс.Диск\n'
                  f'5 - последовательно выполнить все операции:\n'
                  f'\t\tзадать № пользователя\n\t\tсоздать папку\n\t\tзаписать все фото\n\t\tсоздать файл со списком\n'
                  f'{line}\n'
                  f'Введите команду: ', sep='', end='')
            command = input().strip()
            if command == '0':
                print('До свидания!')
                return
            if command in func_dict.keys():
                func_dict[command]()
            else:
                print('Неизвестная команда')


if __name__ == '__main__':
    # для получения токена для доступа к яндекс.диску для этого приложения (client_id=51536362) формируем ссылку:
    # https://oauth.vk.com/authorize?client_id=51536362&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=stats,offline,photos&response_type=token&v=5.131
    # токен берем из адресной строки ответа на переданноу ссылку из параметра "acsess_token=..."
    # токен для доступа к яндекс.диску считываем из файла token_yandex_disk.txt
    try:
        token_yandex = ''
        with open('token_yandex_disk.txt', 'r', encoding='utf-8') as ftoken_yandex:
            token_yandex = ftoken_yandex.read().strip()
    except Exception as err:
        print_info(f'Не удалось считать токен для доступа к Яндекс.Диску')

    # токен для в контакте записан в файл token.txt
    try:
        token = ''
        with open('token.txt', 'r', encoding='utf-8') as tokfile:
            token = tokfile.read().strip()
    except Exception as err:
        print_info(f'Не удалось считать токен для доступа к "В Контакте"')

    # текущая версия api 5.131, теперь всегда будем указывать ее, чтобы изменения api не нарушили код программы
    vk_client = VkUser(token, '5.131')
    ya = YandexDisk(token_yandex)
    user = UserOperations()
    user.react_on_kbd()