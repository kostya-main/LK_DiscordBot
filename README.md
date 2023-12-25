# Личный кабинет в виде Discord бота

Данный бот имеет базовый функционал для конечного пользователя:
- Регистрация
- Смена скинов
- Смена плащей
- Смена ников
- Смена пароля
- Реализация магазина (Интеграция с `ЮKassa`)

# Установка

Для работы бота понадобится: `Python` не новее 3.11, `Mariadb` версии 10.11, `Nginx`, `GravitLauncher` не старее 5.5.  

Установка зависимостей Python: (В директории с ботом)

```
pip install -r requirements.txt
```

Запуск бота:  

```
python main.py
```

Конфигурация Nginx:

```
upstream gravitlauncher {
    server 127.0.0.1:9274;
}
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
server {
    listen 443 ssl http2;
    server_name api.ВАШ ДОМЕН.ru;
    charset utf-8;
    #access_log  /var/log/nginx/launcher.access.log main;
    #error_log  /var/log/nginx/launcher.error.log notice;
    keepalive_timeout   70;    
    root /ПУТЬ/ДО/updates;

    
    ssl_certificate /etc/nginx/ssl/sertificat.pem;
    ssl_certificate_key /etc/nginx/ssl/cert.key;
    ssl_client_certificate /etc/nginx/ssl/test.pem;
    ssl_verify_client on;
    
    location / {
    }
    location /api {
        proxy_pass http://gravitlauncher;
        proxy_http_version 1.1;
        real_ip_header X-Forwarded-For;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /skinapi/ {
        proxy_pass http://127.0.0.1:8123/;
        proxy_http_version 1.1;
        real_ip_header X-Forwarded-For;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /skinapi/pay_check {
        allow 185.71.76.0/27;
        allow 185.71.77.0/27;
        allow 77.75.153.0/25;
        allow 77.75.156.11;
        allow 77.75.156.35;
        allow 77.75.154.128/25;
        allow 2a02:5180::/32;
        deny all;
    }
    location ~ /\.(?!well-known).* {
        deny all;
    }
}

```