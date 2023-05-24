# Graylog alerter 
Part of it-service.io alert system

------
[РУС](docs/ru/README.md) | [ENG](README.md)

## Prerequisites
 - Graylog
 - custom middleware (not part of this repository)
 - Kafka
 - Redis

------

## Install

```shell
git clone https://github.com/nekonekun/critical/
cd critical
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

------

## Run

```shell
critical /path/to/etc/handler_name.yml --kafka-server localhost --kafka-topic critical
``` 

------

## Configure

Handlers can be configured only via configuration files.

See [Configuration](docs/en/Configuration.md) for information and examples.

------

## Telegram helper-bot

Little bot to simplify Redis interactions (we need it to make our [Dynamic filters](docs/en/Configuration.md#4-dynamic-filters) work)

### Run

```shell
critical-bot --bot-token 1234567890:AAAAAbbbbbCddEEff0GhhIIII0J-K0llllM --redis-host 127.0.0.1 --redis-port 6379 --redis-db 0 
```

### Usage
`/filter smth` to filter out `smth` pattern (could be regexp too)

`/delete smth` to delete `smth` pattern from filter rules

`/show` to show all filtered patterns

------

## GELF message format

 - `version`: str: GELF version
 - `timestamp`: int
 - `host`: str 
 - `short_message`: str
 - `level`: int
 - `full_message`: str: message plus timestamp
 - `_level`: int: same as level
 - `_gl2_remote_ip`: str
 - `_gl2_remote_port`: int
 - `_gl2_message_id`: str: unique message ID
 - `_kafka_topic`: str: custom field
 - `_source`: str: same as host
 - `_message`: str: same as short_message
 - `_gl2_source_input`: str: unique input ID
 - `_full_message`: str: same as full_message
 - `_facility_num`: int
 - `_forwarder`: str: output type, we will se org.graylog2.outputs.GelfOutput here
 - `_gl2_source_node`: str: node ID in UUID format
 - `_id`: str: unique ID in UUID format
 - `_facility`: str
 - `_timestamp`: str: timestamp in ISO format with timezone
------

## Log entry route
Briefly: Graylog > Kafka > This script > Destination

To see extended version, look [here](docs/en/LogEntryRoute.md).
