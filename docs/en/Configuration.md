# Configuration

This script can be configured only via YAML configuration files.

Less theory, more practice? Just jump to [example](#example) section. 

## Basics

 - File sections can be arranged in any order.
 - Consumer Specification, Senders and Formatter sections are mandatory
 - Static filters, Dynamic filters and Name sections are optional


## Sections

### 1. Consumer specification
 - Key: `consumer_specification`
 - Value of `consumer_specification` field will be passed to consumer. For KafkaConsumer it should be Kafka topic name.
### 2. Name
 - Key: `name`
 - Handler name. This name will be used to make Kafka `group ID`
### 3. Senders
 - Key: `senders`
 - Multiple senders are allowed, so senders' section is a list
 - Each sender configuration must have `class` field
 - Two sender are implemented by now
 - #### TelegramSender
 - Two parameters: `token` and `receivers`
 - `token`: Telegram Bot API token
 - `receivers`: list of chat_ids
 - If bot could not send a message to receiver ('coz of privacy settings or something like that) -- message will be ignored, but bot will try to send message next time. 
 - #### MailSender
 - Eight parameters: `hostname`, `port`, `username`, `password`, `use_tls`, `sender`, `subject` and `receivers`
 - `hostname`: SMTP server hostname
 - `port`: SMTP server port
 - `username`: SMTP username
 - `password`: SMTP password
 - `use_tls`: optional, True by default. Set False to disable TLS 
 - `sender`: Sender
 - `subject`: Default subject. Will be used if no "Subject: " header is present in message
 - `receivers`: list of e-mails addresses
### 4. Formatter
 - Key: `formatter`
 - Each handler can have only one Formatter
 - Formatter configuration must have `class` field
 - Two formatters are implemented by now
 - #### CopyFieldFormatter
 - One parameter: `field`
 - `field`: one of Graylog Extended Log Format fields
 - #### SimpleMailFormatter
 - Three parameters: `subject_field`, `body_field` and `format`
 - `subject_field`: one of GELF fields to be copied into e-mail "Subject: " field
 - `body_field`: one of GELF fields to be copied into e-mail body
 - `format`: message template, optional, defaults to `Subject: {subject}\n\n{body}`
### 5. Static Filters
 - Key: `static_filters`
 - Multiple static filters are allowed, so static filters' section is a list
 - Static filters are applied together (i.e. as they have AND between them)
 - Order doesn't matter
 - It's good idea to have little allowing filters and a bunch of denying
 - Static filters are applied first
 - Static filters have access on all GELF fields
 - Each static filter configuration must have `class` field
 - Three static filters are implemented by now
 - #### IPSourceFilter
 - Three parameters: `prefixes`, `ips` and `exclude`
 - `prefixes`: list of IPv4 prefixes
 - `ips`: list of IPv4 IPs
 - `exclude`: boolean value, False by default. Set True to exclude specified prefixes/IPs 
 - #### MessageBodyFilter
 - Two parameters: `pattern` and `exclude`
 - `pattern`: substring to be searched in `full_message` field
 - `exclude`: boolean value, False by default. Set True to exclude messages that contain specified pattern
 - ####MessageBodyAnyFilter
 - Nearly same as above, but with multiple patterns to search
 - Message will be allowed/denied if any of patterns are present in `full_message` field
 - Two parameters: `patterns` and `exclude`
 - `patterns`: list of substrings
 - `exclude`: boolean value, False by default. Set True to exclude messages that contain any of specified patterns

### 6. Dynamic filters
 - Key: `dynamic_filters`
 - Multiple dynamic filters are allowed, so dynamic filters' section is a list
 - Dynamic filters are exclud'ish by default
 - Dynamic filters are applied last
 - Dynamic filter decisions are based on receiver (e.g. `tg_123456789` or `mail_nekonekun@gmail.com`)
 - Dynamic filters have access only on outgoing message text (after formatting)
 - Each dynamic filter configuration must have `class` field
 - Only one dynamic filter is implemented by now
 - #### RedisExcludePattern
 - Three parameters: `host`, `port` and `db`
 - `host`: Redis host
 - `port`: Redis port (optional)
 - `db`: Redis database number (optional). Defaults to 0
 - Redis structure looks like ```key: set_of_patterns```, with key described in previous section
# Example
 In this example handler will:
 - Pass topic name `critical-topic` to consumer
 - Catch messages from all devices within 10.0.0.0/8 subnet, except annoying 10.0.0.188 and 10.120.16.240
 - Discard messages if any unimportant pattern such as `IGMPSNOOPING-6-NO_IGMP_QUERIER`, `SPANTREE-6-INTERFACE` etc. would be found  
 - Take `short_message` field from the GELF-message
 - Test it against patterns from redis database (handler will look for keys tg_150897551 and tg_-1001234567890)
 - If no patterns from redis will be found, messages will be sent to @nekone and to our Alerting chat
```yaml
name: EVERYTHING
consumer_specification: critical-topic 

senders:
  - class: TelegramSender
    token: 1234567890:AAAAAbbbbbCddEEff0GhhIIII0J-K0llllM
    receivers:
      - 150897551  # @nekone
      - -1001234567890  # Alerting chat

static_filters:
  - class: SourceIPFilter
    prefixes:
      - 10.0.0.0/8
  - class: SourceIPFilter
    ips:
      - 10.0.0.188
      - 10.120.16.240
    exclude: true
  - class: MessageBodyAnyFilter
    patterns:
      - IGMPSNOOPING-6-NO_IGMP_QUERIER
      - GMP-4-IGMP_QUERY_VERSION_CONFIGURED_DISCREPANCY
      - SPANTREE-6-INTERFACE
      - SPANTREE-6-STABLE_CHANGE
      - SECURITY-6-SSH_CLIENT_CONNECTING
      - SECURITY-6-SSH_CLIENT_DISCONNECTED
    exclude: True

dynamic_filters:
  - class: RedisExcludeRegexp
    host: 127.0.0.1
    db: 3

formatter:
  class: CopyFieldFormatter
  field: short_message
```
[<< Back](../../README.md)