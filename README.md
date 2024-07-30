## Содержание
- [Вступление](#вступление)
- [Диаграмма](#диаграмма)
- [Модели](#модели)
  - [User](#user)
  - [Device](#device)
  - [Backup Tokens](#backup-tokens)
- [Эндпоинты](#эндпоинты)
  - [Auth](#auth)
  - [Two Factor Authentication](#two-factor-authentication)
  - [Users](#users)
  - [Tasks](#tasks)
- [Crud](#crud)
- [Core](#core)
## Запуск
- [Запуск через docker-compose](#запуск-через-docker-compose)

## Известные проблемы
- [Известные проблемы](#известные-проблемы)


### **[Вступление](#вступление)**
Это приложение - это mockup - сервис аутентификации, разработанный с использованием FastAPI. В нем представлен базовый вариант аутентификации
с помощью JWT - токенов и возможностью подключить двухфакторную авторизацию (или TFA - Two Factor Authentication).

**Двухфакторная авторизация**

Двухфакторную авторизацию можно включить двумя следующими способами:
* Email (OTP - токен будет отправлен по почте)
* Генератор кодов (при активации будет доступен QR - код, который можно просканировать и загрузить многоразовый OTP - токен в
любое приложение для авторизации, например Google Authenticator)

В представленном сервисе доступна только TOTP - версия OTP - протокола валидации, которая базируется на timestamp'е и
персональном ключе каждого пользователя.


**Backup токены**

При активации TFA, вне зависимости от выбранного типа авторизации, на почту будет направлено письмо с 5 backup - токенами,
которыми можно воспользоваться в случае если QR - код был утерян или если по какой-то причине невозможно получить токен.
Данные токены - одноразовые, если все токены израсходованы - восстановить QR - код для того же пользователя без сброса невозможно.

**Email - сервис**

Отправка писем осуществляется с помощью yagmail, настроенного на почту с помощью app password внутри Gmail. Задачи на
отправку писем отправляются в брокер RabbitMQ, где уже перенаправляются в Celery для обработки.

**Сервисы**

Все сервисы разворачиваются с помощью Docker, непосредственно развертывание происходит с помощью docker-compose. Для
хранения данных пользователя используется PostgreSQL, в качестве брокера очереди - RabbitMQ, Celery используется для обработки
и распределения задач, а Redis используется как persistent бэкенд, хранящий результаты задач. При развертывании сервиса
так же доступен сервис Flower для мониторинга задач в Celery и интерактивная документация для FastAPI, в которой можно
проверить часть функционала. Порты, адреса и другие параметры для данных сервисов задаются в [.env-файле](./deploy/.env),
дефолтные значения для каждого сервиса можно увидеть в таблице ниже:


| Сервис            | Название контейнера   | Порт  |
|-------------------|-----------------------|-------|
| **FastAPI**       | fastapi_auth          | 8001  |
| **PostgresDB**    | fastapi_auth-db       | 5454  |
| **Redis**         | fastapi_auth-cache    | 6389  |
| **RabbitMQ**      | fastapi_auth-rabbitmq | 15672 |
| **Celery worker** | fastapi_auth-celery   |       |
| **Flower**        | fastapi_auth-flower   | 5557  |


### **[Диаграмма](#диаграмма)**

<img src="https://github.com/user-attachments/assets/560c380d-00be-48f2-90ae-5491abffc7cb" alt="image" style="width:700px;"/>

### **[Модели](#модели)**

Модель User имеет One to One связь с моделью Device. Device имеет One to Many связь с моделью BackupTokens.

#### [User](#user)

* `full_name` - имя пользователя
* `email` - логин пользвателя; так же используется для отправки письма
* `hashed_password` - пароль пользователя; после успешной регистрации хешируется
* `tfa_enabled` - true / false поле для обозначения флага доступности TFA для этого пользователя

#### [Device](#device)

* `user_id` - ID пользователя
* `key` - здесь хранится зашифрованная версия OTP - ключа пользователя
* `device_type` - это поле определяет тип устройства, которое будет использоваться при авторизации: `email` или `code_generator`

#### [Backup Tokens](#backup-tokens)

* `device_id` - ID устройства
* `token` - случайно генерируемый TOTP - token


### **[Эндпоинты](#эндпоинты)**

Эндпоинты можно частично протестировать через FastAPI Swagger. Он будет доступен по адресу `/docs` на том компьютере,
где вы развернули сервис (по умолчанию `localhost:8001/docs`). Ниже будут указаны curl - команды, которыми можно установить,
получить и сменить как JWT - токены, так и QR - код.

#### [Auth](#auth)

* `/api/v1/auth/signup`

    **POST** - Создает нового пользователя.

    Ключ `device` требуется только если `tfa_enabled` = `true`;

    `device_type` должен быть либо `email`, либо `code_generator`

    **Пример тела запроса**

    ```json
    {
        "email": "user@example.com",
        "tfa_enabled": true,
        "full_name": "string",
        "password": "123456",
        "device": {
            "device_type": "email"
        }
    }
    ```

    **Пример curl - запроса** (`--output` сохранит изображение, только если тип устройства был указан как `code_generator`)

    ```shell
    curl -X "POST" \
    "http://localhost:8001/api/v1/auth/signup" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d "{
    "email": "user@example.com",
    "tfa_enabled": true,
    "full_name": "string",
    "password": "123456",
    "device": {
        "device_type": "email"
    }
    }" --output my_qrcode.jpg
    ```

* `/api/v1/auth/login`

    **POST** - Аутентификация нового пользователя

    **Тело запроса**

    ```
    EMAIL
    PASSWORD
    ```

    **curl**

    ```shell
    curl -X "POST" \
    "http://localhost:8001/api/v1/auth/login" \
    -H "accept: application/json" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=&username={{ EMAIL }}&password={{ PASSWORD }}&scope=&client_id=&client_secret="
    ```

    **Тело ответа**
    ```
     ACCESS_JWT_TOKEN
     REFRESH_JWT_TOKEN
    ```

* `/api/v1/auth/test-token`

    **GET** - Проверить, авторизован ли пользователь, с помощью полученного на предыдущем шагу JWT - токена.

    **Тело запроса**
    ```
     ACCESS_JWT_TOKEN
    ```

    **Пример curl - запроса**

    ```shell
    curl -X "GET" \
    "http://localhost:8001/api/v1/auth/test-token" \
    -H "accept: application/json" \
    -H "Authorization: Bearer {{ ACCESS_JWT_TOKEN }}"
    ```


* `/api/v1/auth/refresh`

    **POST** - при предоставлении `REFRESH_JWT_TOKEN` возвращает новый `ACCESS_JWT_TOKEN`

    **Тело запроса**

    ```json
    {
        "refresh_token": "{{ REFRESH_JWT_TOKEN }}"
    }
    ```

    **Пример curl - запроса**

    ```shell
    curl -X "POST" \
    "http://localhost:8001/api/v1/auth/refresh" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d "{
    "refresh_token": "{{ MY_JWT_REFRESH_TOKEN }}"
    }"
    ```



#### [Two Factor Authentication](#two-factor-authentication)

* `/api/v1/tfa/login_tfa?tfa_token=`

    **POST** - Это второй шаг после авторизации для пользователей со включенной TFA.
    Для этого шага необходимо иметь TOTP - токен и временный JWT - токен, полученный после прохождения этапа `Authorization`

    **Пример curl - запроса**

    ```shell
    curl -X "POST" \
    "http://localhost:8001/api/v1/tfa/login_tfa?tfa_token={{ MY_TOTP_TOKEN }}" \
    -H "accept: application/json" \
    -H "Authorization: Bearer {{ PRE_TFA_JWT_ACCESS_TOKEN }}" \
    -d ""
    ```

* `/api/v1/tfa/recover_tfa?tfa_backup_token=`

    **POST** - Этот шаг необходим для пользователей с включенным TFA, которые не получили TOTP-токен, но получили backup-токены.
    На этом шагу они могут использовать эти токены для воостановления доступа.  Для этого шага необходимо иметь
    временный JWT - токен, полученный после прохождения этапа `Authorization`.

    **Пример curl - запроса**

    ```shell
    curl -X "POST" \
    "http://localhost:5555/api/v1/tfa/recover_tfa?tfa_backup_token={{ MY_BACKUP_TOTP_TOKEN }}" \
    -H "accept: application/json" \
    -H "Authorization: Bearer {{ MY_PRE_TFA_JWT_ACCESS_TOKEN }}" \
    -d ""
    ```

* `/api/v1/tfa/get_my_qrcode`

    **GET** - Эндпоинт для повторного получения QR - кода (только для пользователей с типом устройства `code_generator`)

    **Пример curl - запроса**

    ```shell
    curl -X "GET" \
    "http://localhost:5555/api/v1/tfa/get_my_qrcode" \
    -H "accept: application/json" \
    -H "Authorization: Bearer {{ MY_JWT_ACCESS_TOKEN }}"  --output my_recovered_qr_code.png
    ```

* `/api/v1/tfa/enable_tfa`

    **PUT** - Включение TFA для пользователей, которые не выбрали этот режим при регистрации. `device_type` должен быть
    либо `email`, либо `code_generator`

    **Тело запроса**

    ```json
    {
        "device_type": "code_generator"
    }
    ```

    **Пример curl - запроса** (`--output` сохранит изображение, только если тип устройства был указан как `code_generator)

    ```shell
    curl -X "PUT" \
    "http://localhost:8001/api/v1/tfa/enable_tfa" \
    -H "accept: application/json" \
    -H "Authorization: Bearer {{ MY_JWT_ACCESS_TOKEN }}" \
    -H "Content-Type: application/json" \
    -d "{
    "device_type": "code_generator"
    }" --output my_new_qr_code.jpg
    ```


#### [Users](#users)

* `/api/v1/users/users`

    **GET** - Эндпоинт, не требующий авторизации и возвращающий список всех пользователей в базе данных.

    **curl**

    ```shell
    curl -X "GET" \
    "http://localhost:8001/api/v1/users/users" \
    -H "accept: application/json"
    ```

#### [Tasks](#tasks)

* `/api/v1/tasks/test-celery`

    **GET** - Эндпоинт для проверки функции отправки почты.

    **Тело запроса** (%40 в запросе равноценно @)

    ```
     email_address%40mail.service
    ```

    **Пример curl - запроса**

    ```shell
    curl -X "GET" \
  "http://localhost:8001/api/v1/tasks/test-celery?email_addr=email_address%40mail.service" \
  -H "accept: application/json"
    ```

* `/api/v1/tasks/taskstatus?task_id=`

    **GET** - Эндпоинт для получения статуса задачи. `?task_id` вовращается эндпоинтом ``/api/v1/tasks/test-celery`.

    **curl**

    ```shell
    curl -X "GET" \
    "http://localhost:8001/api/v1/tasks/taskstatus?task_id={{ TASK_ID }}" \
    -H "accept: application/json"
    ```

### **[Crud](#crud)**
Модули в этой части сервиса отвечают за взаимодействие с базой данных.

### **[Core](#core)**
Модули в этой части сервиса отвечают за общую логику работы программы.


## [Запуск через docker-compose](#запуск-через-docker-compose)

Чтобы запустить все сервисы, из корневой папки сервиса необходимо написать:

```shell
docker-compose -f deploy/docker-compose.yaml up -d
```

`docker-compose` автоматически соберет все необходимые образы и запустит все сервисы самостоятельно на указанных портах.

FastAPI - сервер по умолчанию запускается на порту `8001`, интерактивная документация FastAPI доступна по адресу
http://localhost:8001/docs#/

---

Чтобы получить логи основного контейнера, в терминале можно написать:
```shell
dockerfiles logs --tail 200 -f fastapi_auth
```

__________
__________

## [Известные проблемы](#известные-проблемы)

* Не все эндпоинты можно проверить через Swagger - это ограничение FastAPI, через curl все запросы отрабатывают
* TOTP - токены продолжают отправляться при выборе устройства email - это необходимо для возможности восстановить доступ
* Отсутствуют тесты
* Отсутствует логирование
