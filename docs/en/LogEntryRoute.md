# Log entry route
1. Log entry gets into one of Graylog Inputs
2. Graylog adds new field "kafka_topic" with value of Kafka topic name according to Pipeline rules
3. Log entry gets forwarded to our custom middleware according to Output rules (we use GelfOutput)
4. Our custom middleware listens Graylog's stream, splits it by "\x00" byte, gets topic name, and writes message to specific Kafka topic
5. This script apply filters, formats message to string and sends it to specified destination

[<< Back](../../README.md)