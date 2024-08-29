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
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer,SerializationContext, MessageField


class User(object):
    """
    User record
    Args:
        name (str): User's name
        favorite_number (int): User's favorite number
        favorite_color (str): User's favorite color
    """
    def __init__(self, Nama_Emiten=None, Nama_Customer=None, Jumlah_Transaksi=None, Waktu=None):
        self.Nama_Emiten = Nama_Emiten
        self.Nama_Customer = Nama_Customer
        self.Jumlah_Transaksi = Jumlah_Transaksi
        self.Waktu = Waktu



def dict_to_user(obj, ctx):
    """
    Converts object literal(dict) to a User instance.
    Args:
        obj (dict): Object literal(dict)
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    """
    if obj is None:
        return None

    return User(Nama_Emiten=obj['Nama_Emiten'],
                Nama_Customer=obj['Nama_Customer'],
                Jumlah_Transaksi=obj['Jumlah_Transaksi'],
                Waktu=obj['Waktu'])


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

    sr_conf = { 'url': 'http://localhost:8081'}

    schema_registry_client = SchemaRegistryClient(sr_conf)

    avro_deserializer = AvroDeserializer(schema_registry_client,
                                         schema_str,
                                         dict_to_user)

    string_deserializer = StringDeserializer('utf_8')

    consumer_conf = {'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
            'key.deserializer': string_deserializer,
            'value.deserializer': avro_deserializer,
            #'ssl.ca.location':'/var/ssl/private/ca.crt',
            'security.protocol':'PLAINTEXT',
            'group.id':'grup-test-client',
            'auto.offset.reset':'earliest',
            #ConsumerTuning
            'fetch.min.bytes':               1,
            'max.poll.interval.ms':          300000,
            'auto.commit.interval.ms':       5000,
            'heartbeat.interval.ms':         3000,
            #'partition.assignment.strategy': 'cooperative-sticky',
            }

    consumer = DeserializingConsumer(consumer_conf)
    consumer.subscribe([topic])
    #dateobj=datetime.strptime(s1,"%Y-%m-%d %H:%M:%S")
    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            user = msg.value()
            if user is not None:
                print("User record {}:\n"
                      "\tNama_Emiten: {}\n"
                      "\tNama_Customer: {}\n"
                      "\tJumlah_Transaksi: {}\n"
                      "\tWaktu: {}\n"
                      .format(msg.key(), user.Nama_Emiten,
                              user.Nama_Customer,
                              user.Jumlah_Transaksi,
                              user.Waktu))
        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == '__main__':
    main()



