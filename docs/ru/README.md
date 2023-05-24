# Graylog alerter 
Part of it-service.io alert system

------
[РУС](README.md) | [ENG](../../README.md)

## Требования
 - Graylog
 - свой промежуточный обработчик (не часть этого репозитория)
 - Kafka
 - Redis

------

## Установка

```shell
git clone https://github.com/nekonekun/critical/
cd critical
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

------

## Запуск

```shell
critical /path/to/etc/handler_name.yml --kafka-server localhost --kafka-topic critical
``` 

------

## Настройка

Обработчики настраиваются только с помощью конфигурационных файлов

В разделе [Настройка](Configuration.md) есть информация о настройке и пример.

------

## Telegram бот-помощник

Маленький бот для упрощения работы с Redis (он нам нужен чтобы наши [Динамические фильтры](Configuration.md#4-dynamic-filters) работали)

### Запуск

```shell
critical-bot --bot-token 1234567890:AAAAAbbbbbCddEEff0GhhIIII0J-K0llllM --redis-host 127.0.0.1 --redis-port 6379 --redis-db 0 
```

### Использование
`/filter smth` для того, чтобы отфильтровать строку `smth` (можно указывать и регулярное выражение)

`/delete smth` для того, чтобы удалить строку `smth` из списка фильтрации

`/show` для того, чтобы показать список отфильтрованных строк

------

## Формат GELF

 - `version`: строка: версия GELF 
 - `timestamp`: число
 - `host`: строка
 - `short_message`: строка
 - `level`: число
 - `full_message`: строка: время плюс `short_message`
 - `_level`: число: то же самое, что `level`
 - `_gl2_remote_ip`: строка
 - `_gl2_remote_port`: число
 - `_gl2_message_id`: строка: уникальный ID сообщения
 - `_kafka_topic`: строка: добавленное нами поле
 - `_source`: строка: то же самое, что `host`
 - `_message`: строка: то же самое, что `short_message`
 - `_gl2_source_input`: строка: уникальный ID Input'а
 - `_full_message`: строка: то же самое, что `full_message`
 - `_facility_num`: число
 - `_forwarder`: строка: тип Output'а, мы здесь будем видеть org.graylog2.outputs.GelfOutput
 - `_gl2_source_node`: строка: ID Nod'ы в формате UUID 
 - `_id`: строка: уникальный ID в формате UUID 
 - `_facility`: строка
 - `_timestamp`: строка: время в ISO формате с часовым поясом
------

## Путь записи лога
Коротко: Graylog > Kafka > Этот скрипт > Получатель

[Здесь](LogEntryRoute.md) более полная версия
