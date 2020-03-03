##############################################################
# Database format
# POST ID | MATERIAL NAME | CONTAINER NAME | DATE TIME
##############################################################

import psycopg2


class SP5_INTERFACE:

    def __init__(self):
        self.start_date = 'not_defined'
        self.end_date = 'not_defined'
        self.database_name = 'not_defined'
        self.database_user = 'not_defined'
        self.database_password = 'not_defined'
        self.database_host = 'not_defined'
        self.database_port = 'not_defined'
        self.output_file_name = 'not_defined'

    def schedule(self, event_name, event_value, event_id, start_date, end_date, database_name, database_user, database_password,
                 database_host, database_port, output_file_name):
        if event_name == 'INIT':
            return [event_value, None, 0]

        elif event_name == 'TRIGGER':
            # event_id == 1 - request data from start_data to end_data
            if event_id == '1':

                # Connect to database and get data
                con = psycopg2.connect(database=database_name, user=database_user, password=database_password,
                                       host=database_host, port=database_port)

                cur = con.cursor()
                # get data from database using start and end date, and ordered by chassis and time
                # this allows to get the exit time of a post in the next row (which is the entering time of the next post)
                cur.execute("""SELECT * from SP5DATA WHERE DATE_TIME >=%s AND DATE_TIME <= %s ORDER BY VIS, DATE_TIME ASC;""", (start_date, end_date))
                result_lines = cur.fetchall()
                n = cur.rowcount
                print("cur.rowcount: ", n)
                con.close()

                # format data save to file
                #with open('test.csv', 'w') as writeFile:
                with open(output_file_name, 'w') as writeFile:
                    count = 1
                    for row in result_lines:
                        if count < n:
                            line = "{0},{1},{2},{3}\n".format(row[2], row[1], row[4], result_lines[count][4])
                            writeFile.write(line)
                            count += 1

                writeFile.close()

            # event_id == 2 - send data back to MES
            elif event_id == '2':
                print("send data back to MES")

            return [event_value, None, 0]
