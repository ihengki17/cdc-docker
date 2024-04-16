# <div align="center">Confluent CDC on Docker</div>

## <div align="center">Guide</div>

# Introduction

In this demo, you'll walk through the CDC Connector of Oracle and Postgres

---

## Build-up Environment

The following steps will bring you through the process of Confluent Cluster and Database (Oracle and PostgreSQL) on top of container using docker-compose.


### Deploy the Environment

1. Navigate to repo's directory.
   ```bash
   cd cdc-docker
   ```
1. Download and run the container for all of the service (ZooKeeper, Broker, Schema Registry, Kafka Connect, ksqlDB, Control Center, Oracle, PostgreSQL).
   ```bash
   docker-compose up -d
   ```
1. Make sure the container already successful deployed.
   ```bash
   docker ps
   ```
1. If all of the services is already been deployed, CONGRATULATIONS! your cluster already ready to use now.

### Deploy the CDC Connector

1. Access the Control Center using your web browser.
   ```bash
   <hostname/DNS>:9021
   ```
2. Click and access your Cluster.
3. Click tab "Connect" on the left to access your Connect Cluster.
4. Add your Connector using "Upload connector config file".
5. You could use "CDC_Source_Oracle.json" to deploy the Oracle CDC Source connector first.
6. Click "next" at the bottom and click "launch".
7. Go back to "Topic" tab on the left, if you see CDC_CUSTACCOUNT and CDC_CUSTTRANSACTIONS then CONGRATULATIONS! your first Oracle CDC Connector is running well

**Notes**: Do the same thing with for PostgreSQL using "connector_CDC_Postgres_config.json" after you create the table
```sql
CREATE TABLE public.test (
	id varchar NOT NULL,
	"name" varchar NULL,
	telephone_number varchar NULL,
	gender varchar NULL,
	CONSTRAINT test_pk PRIMARY KEY (id)
);
```

### Deploy the Sink Connector

1. Access the Control Center using your web browser.
   ```bash
   <hostname/DNS>:9021
   ```
2. Click and access your Cluster.
3. Click tab "Connect" on the left to access your Connect Cluster.
4. Add your Connector using "Upload connector config file".
5. You could use "Oracle_Sink.json" to deploy the JDBC Sink connector.
6. Click "next" at the bottom and click "launch".
7. Go to your database to see the new table named "account" on your Oracle DB.

### Insert, Update, Delete transactions

1. Access your Oracle Database on Schema "MYUSER" (User and password can be seen on docker-compose.yml)
2. Let's do some action on our table "CUSTACCOUNT" using insert, update and delete
   ```sql
   INSERT INTO MYUSER.CUSTACCOUNT (CUSTOMER_ID, ACCOUNT_ID, ACCOUNT_TYPE, ACCOUNT_OPENING_DATE) VALUES('C105', 'SAV105', 'savings', sysdate);
   UPDATE MYUSER.CUSTACCOUNT SET CUSTOMER_ID='C106', ACCOUNT_TYPE='savings', ACCOUNT_OPENING_DATE=sysdate WHERE ACCOUNT_ID='SAV105';
   DELETE FROM MYUSER.CUSTACCOUNT WHERE ACCOUNT_ID='SAV105';
   ```
3. Do the action one at a time as you could check on another table "account" that can be seen will be mirroring as the source table.

### Execute the performance test

1. You could run the performance test by using this command and change the parameter value to change the behaviour as your real scenario and get the benchmark on your Streaming Cluster
   ```bash
   docker exec broker kafka-producer-perf-test --throughput 100 --record-size 1000 --num-records 10000 --topic perf-test-topic --producer-props linger.ms=1500 batch.size=300000 bootstrap.servers=broker:29092
   ```
2. You could chage the throughput (transaction per sec), record-size (bytes), total num-records (number of records that will be sent) as you fit into your scenario
**Notes**: use -1 on throughput to open the limit for the transactions

### Consume the data

1. You could consume the data through cli using the
   ```bash
   docker exec broker kafka-console-consumer --bootstrap-server broker:29092 --topic perf-test-topic --from-beginning
   ```
2. You could chage the topic that you read as it been produced by the producer-perf-test, Oracle CDC, and PostgreSQL CDC (CDC_CUSTACCOUNT, CDC.public.test)
