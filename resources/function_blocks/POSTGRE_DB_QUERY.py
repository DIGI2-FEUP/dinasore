"""
# ATENTION! First install dependencies (example for Linux): 
# sudo apt install python3-dev libpq-dev
# pip install psycopg2

# Error handling took from: https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
# Error handling must be improved, not working with queries

This block executes the SQL query given to the QUERY variable.

Consider the following table structure for the 3 examples below.
reference_id (integer auto-increment pk) | sensor_id (integer) | actuator_id (integer)

1 - Example to insert without specifying the column names.
This example will auto increment reference_id column.

QUERY:
INSERT INTO reference_values VALUES (1,1,3)


2 - Example to insert specifying the column names, no returning values:
This example will auto increment reference_id column.

QUERY:
INSERT INTO reference_values (sensor_id,actuator_id) VALUES (1,3)
"""

import psycopg2
from psycopg2 import OperationalError, errorcodes, errors
import json

class POSTGRE_DB_QUERY:

    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def schedule(self, event_name, event_value,
                 host, port, user, password, dbname,
                 query):

        if event_name == 'INIT':
            # catch exception for invalid SQL connection
            try:
                # declare a new PostgreSQL connection object
                self.conn = psycopg2.connect(dbname=dbname, 
                    user=user, 
                    password=password,
                    host=host,
                    port=port)
                self.cursor = self.conn.cursor()

            except OperationalError as err:
                print(err)
                # set the connection to 'None' in case of error
                self.conn = None

            finally:
                return [event_value, None, None]

        elif event_name == 'RUN':
            result = None
            if self.conn != None:
                
                # catch exception for invalid SQL statement#
                result = None
                try:
                    self.cursor.execute(query)
                    self.conn.commit()
                    result = self.cursor.fetchall()

                except Exception as err:
                    print(err)
                    # rollback the previous transaction before starting another
                    self.conn.rollback()
                    result = str(err)

                finally:
                    return [None, event_value, result]
            else:
                result = "No active connection to PostgreSQL DB."
                print(result)
                return [event_value, None, result]