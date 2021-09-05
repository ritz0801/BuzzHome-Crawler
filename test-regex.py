import psycopg2
from crawler import facebook
import time
import csv
import unicodedata
from functionUtils import *
from geopy.geocoders import Nominatim
import json



try:
    print('start connection')
    connection = psycopg2.connect(user="postgres",
                                  password="$kie2020$",
                                  host="buzzhome.c1fjqvwcovne.ap-southeast-1.rds.amazonaws.com",
                                  port="5432",
                                  database="buzzhome")
    # connection = psycopg2.connect(user="postgres",
    #                               password="123456",
    #                               host="127.0.0.1",
    #                               port="5432",
    #                               database="buzzhome-dev")

    cursor = connection.cursor()

    selectPostCommand = """
        SELECT id, content , "postLink"
	    FROM public.posts
        where id > 0 and id < 1000
        """

    updatePostCommand = """
       UPDATE public.posts
        SET "isForRenter"=%s,price=%s,district=%s,lng=%s,lat=%s
        WHERE id=%s
        """
    cursor.execute(selectPostCommand)
    post = cursor.fetchall()
    sumPost= len(post)
    print(sumPost)


    count = 0
    countSuccess = 0
    countFailure = 0
    for postItem in post:
        count = count + 1
        print("count: ", count, "/", sumPost)
        try:
            id = postItem[0]
            content = postItem[1]
            print("content: ", content)
            print ("post link: ", postItem[2])
            content = unicodedata.normalize('NFKC', content)
            
            # price = detectPrice( content)
            # print ("********* PRICE: ", price)

            encodedContent = unicodedata.normalize('NFD', content).encode('ascii', 'ignore') # bo dau tieng Viet
            encodedContent = encodedContent.decode('ISO-8859-1')
            
            # isForRenter = checkIsForRenter(encodedContent)
            # print ("********* IS FOR RENTER: ", isForRenter)
            
            # location = detectDistrict({}, content, encodedContent)
            # print ("********* LOCATION: ", location)

            address = detectAddress(content)

            # # get lng lat from address
            # lat = 10.746903
            # lng = 106.676292
            # geolocator = Nominatim(user_agent="buzzhome")
            # geoFromLocation = geolocator.geocode(location)
            # try:
            #     lat = geoFromLocation.latitude
            #     lng = geoFromLocation.longitude
            # except Exception as e:
            #     lat = 10.746903
            #     lng = 106.676292
            # print("Latitude : ", lat, "Longitude: ", lng)
            # cursor.execute(updatePostCommand, (isForRenter, price, location, lng, lat, id))
            connection.commit()
            countSuccess = countSuccess + 1
        except Exception as e:
            print("error when update post: ", e)
            countFailure = countFailure + 1

    print("RESULT: sum = ", sumPost, ", success = ", countSuccess, ", failure = ", countFailure)

    # connection.commit()

except (Exception, psycopg2.Error) as error:
    print("Error: ", error)
finally:
    # closing database connection.
    if(connection):
        cursor.close()
        connection.commit()
        connection.close()
        print("PostgreSQL connection is closed")