#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# This is a simple example of the SerializingProducer using Avro.
#
from six.moves import input

from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from faker import Faker
from faker.providers import DynamicProvider
from datetime import datetime
import time

emiten_provider = DynamicProvider(
     provider_name="emiten",
     elements=["credit", "debit"],
)

fake = Faker()

class User(object):
    """
    User record
    Args:
        name (str): User's name
        favorite_number (int): User's favorite number
        favorite_color (str): User's favorite color
        address(str): User's address; confidential
    """
    def __init__(self, Nama_Emiten, Nama_Customer, Jumlah_Transaksi, Waktu):
        self.Nama_Emiten = Nama_Emiten
        self.Nama_Customer = Nama_Customer
        self.Jumlah_Transaksi = Jumlah_Transaksi
        self.Waktu = Waktu


def user_to_dict(user, ctx):
    """
    Returns a dict representation of a User instance for serialization.
    Args:
        user (User): User instance.
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    Returns:
        dict: Dict populated with user attributes to be serialized.
    """
    return dict(Nama_Emiten=user.Nama_Emiten,
                Nama_Customer=user.Nama_Customer,
                Jumlah_Transaksi=user.Jumlah_Transaksi,
                Waktu=user.Waktu)


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def main():
    topic = 'test_topic'

    schema_str = """
      {
        "fields": [
      {
        "name": "Nama_Emiten",
        "type": "string"
      },
      {
        "name": "Nama_Customer",
        "type": "string"
      },
      {
        "name": "Jumlah_Transaksi",
        "type": "double"
      },
      {
        "name": "Waktu",
        "type": "string"
      }
        ],
    "name": "testrecordtransaksi",
    "type": "record"
  }
    """
    schema_registry_conf = {'url': 'http://localhost:8081'}

    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer_conf = {'auto.register.schemas':True,
                            'use.latest.version':False
                            }

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     user_to_dict,
                                     avro_serializer_conf)

    producer_conf = { 'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
                      #'ssl.ca.location':'/var/ssl/private/ca.crt',
                      'security.protocol':'PLAINTEXT',
                      'key.serializer': StringSerializer('utf_8'),
                      'value.serializer': avro_serializer,
                      ##Producer-Tune-Variable##
                      'batch.size':'16384',
                      'linger.ms':'10',
                      'compression.type':'none',
                      'acks':'all',
                      'enable.idempotence':'false',
                      'retries':'2146473847',
                      'delivery.timeout.ms':'120000',
                      'max.in.flight.requests.per.connection':'5',
                      ##########################
                      }

    producer = SerializingProducer(producer_conf)

    print("Producing user records to topic {}. ^C to exit.".format(topic))
    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        now = datetime.now()
        fake.add_provider(emiten_provider)
        user_nama_emiten = fake.emiten()
        user_nama_customer = fake.name()
        user_jumlah_transaksi = fake.pyint(min_value=10, max_value=5000)*1000
        user_waktu = now.strftime("%Y-%m-%d %H:%M:%S")
        message_key = fake.unique.uuid4()
        user = User(Nama_Emiten=user_nama_emiten,
                    Nama_Customer=user_nama_customer,
                    Jumlah_Transaksi=user_jumlah_transaksi,
                    Waktu=user_waktu)
        print("Producing.....")
        producer.produce(topic=topic, key=message_key, value=user,
                         on_delivery=delivery_report)
        print("\nFlushing records...")
        producer.flush()
        time.sleep(10)


if __name__ == '__main__':
    main()


