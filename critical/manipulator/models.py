import datetime
import ipaddress
import uuid

from pydantic import BaseModel, Field, Extra


class GELFMessage(BaseModel):
    version: str
    timestamp: datetime.datetime
    host: str
    short_message: str
    level: int
    full_message: str
    level_: int = Field(..., alias='_level')
    gl2_remote_ip_: ipaddress.IPv4Address = Field(..., alias='_gl2_remote_ip')
    gl2_remote_port_: int = Field(..., alias='_gl2_remote_port')
    gl2_message_id_: str = Field(..., alias='_gl2_message_id')
    kafka_topic_: str = Field(..., alias='_kafka_topic')
    source_: str = Field(..., alias='_source')
    message_: str = Field(..., alias='_message')
    gl2_source_input_: str = Field(..., alias='_gl2_source_input')
    full_message_: str = Field(..., alias='_full_message')
    facility_num_: int = Field(..., alias='_facility_num')
    forwarder_: str = Field(..., alias='_forwarder')
    gl2_source_node_: uuid.UUID = Field(..., alias='_gl2_source_node')
    id_: uuid.UUID = Field(..., alias='_id')
    facility_: str = Field(..., alias='_facility')
    timestamp_: datetime.datetime = Field(..., alias='_timestamp')

    class Config:
        extra = Extra.allow
