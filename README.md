# Личный кабинет в виде Discord бота

Данный бот имеет базовый функционал для конечного пользователя:
- Регистрация
- Смена скинов
- Смена плащей
- Смена ников
- Смена пароля
- Реализация магазина (Интеграция с `ЮKassa`)
- Создание бан листа (подерживается плагин `AdvancedBan`)
- И многое другое...

Команды бота подрузомивают что вы будете общаться с ним через личные сообщения, так что не переживайте что вам будут мешать. 

### Примеры оформления

![0](https://github.com/kostya-main/LK_DiscordBot/assets/65069020/9138f1f2-8e32-4f47-b773-bccb0a514255)
![2](https://github.com/kostya-main/LK_DiscordBot/assets/65069020/4c4835c0-6cdb-4f04-a721-46a5c59b2c3f)
![3](https://github.com/kostya-main/LK_DiscordBot/assets/65069020/87127d74-b823-43dd-b442-ee35738af844)

# Установка

Для работы бота понадобится: 
- `Python` не новее 3.11
- `Mariadb` версии 10.11
- `Nginx`(не обязательный но желательный)
- `AuroraLauncher`

### Установка зависимостей Python (В директории с ботом)

```
pip install -r requirements.txt
```

### Запуск бота

```
python main.py
```

### База данных

Все нужные для работы таблицы описанные в файле [bdCreate.sql](https://github.com/kostya-main/LK_DiscordBot/blob/aurora-launcher/bdCreate.sql) (Включая и те которые нужны GravitLauncher)

### Настройка Nginx

Конфигурация вашего домена описана в файле [nginx.conf](https://github.com/kostya-main/LK_DiscordBot/blob/aurora-launcher/nginx.conf)

### Настройка AuroraLauncher

Способ авторизации `json`. Пример конфигурации:

```
auth:
  {
    type: json
    authUrl: https://api.ВАШ_ДОМЕН.ru/authorization/auth
    joinUrl: https://api.ВАШ_ДОМЕН.ru/authorization/join
    hasJoinedUrl: https://api.ВАШ_ДОМЕН.ru/authorization/hasJoined
    profileUrl: https://api.ВАШ_ДОМЕН.ru/authorization/profile
    profilesUrl: https://api.ВАШ_ДОМЕН.ru/authorization/profiles
  }
injector:
  {
    skinDomains: [
      "api.ВАШ_ДОМЕН.ru"
    ]
  }
```

### Настройка ЮKassa

В настройках `HTTP-уведомления` должны быть выставлены данные параметры:

![1](https://github.com/kostya-main/LK_DiscordBot/assets/65069020/097c462f-6af0-4363-882f-1fdf000cf49b)

# Конфигурация

Все настройки бота размещены в папке `conf`.  
- `settings.yaml` - Основная настройка бота. **Обязательно посмотрите его!!!!!!**
- `shop.yaml` - Настройка магазина. По умолчанию выключен.


