import psycopg2
from crawler import facebook
import time
import csv


try:
    print('start connection')
    connection = psycopg2.connect(user="postgres",
                                  password="123456",
                                  host="localhost",
                                  port="5432",
                                  database="buzzhome")
    # connection = psycopg2.connect(user="postgres",
    #                               password="123456",
    #                               host="127.0.0.1",
    #                               port="5432",
    #                               database="buzzhome-dev")

    cursor = connection.cursor()
    print('start crawling')
    fb = facebook(depth=1)
    fb.login()
    if fb.verifyLogin():
        print("login successful")
    else:
        print("login failed")
        exit()

    with open('group.txt') as csv_file:
            groupName = []
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                groupName.append(row[0])
            # print(groupName)
    
    while True:
        for group in groupName:
            print("Crawling group: ", group)

            isTest = False
            fb.group(group, isTest)
            fb.write2DBOnlyNew(cursor, connection)
            #fb.write2File('output.txt')
        print("waiting for next loop...")
        time.sleep(2*60*60)

    print("Close driver")
    fb.driver.close()

except (Exception, psycopg2.Error) as error:
    print("Error pgadmin: ", error)
finally:
    # closing database connection.
    if(connection):
        cursor.close()
        connection.commit()
        connection.close()
        print("PostgreSQL connection is closed")