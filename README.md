Для запуска программы нужно создать 2 файла:

    1. файл token.txt, в этот файл записывается токен для доступа к сети 
"В Контакте" для приложения. Номер приложения client_id=51536362
в браузере в адрес страницы вписываем ссылку:
https://oauth.vk.com/authorize?client_id=51536362&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=stats,offline,photos&response_type=token&v=5.131
токен берем из адресной строки ответа на переданную ссылку из параметра "acsess_token=..."

    2. файл token_yandex_disk.txt, в этот файл записывается токен для 
доступа к Яндекс.Диску


