import psycopg2
from crawler import facebook
import time
import csv
import unicodedata
from functionUtils import *
from geopy.geocoders import Nominatim


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
        SELECT id, content , "postLink", "timeStamp", "createdAt"
	    FROM public.posts
        where "timeStamp" like '%Yester%'
        """
        #  where id >= 17000 and id < 18113
        # where id >= 15000 and id < 17000
        #  where id = 10314

    selectCommentCommand = """
        SELECT id, time, "createdAt"
	    FROM public.comments
        where (time like '%now%' 
            or time like '%hr%'
            or time like '%mi%'
            or time like '%Yester%') and id = 1444
        """

    deletePostCommand = """
        DELETE
	    FROM public.posts
        where id = %s
        """
        
    selectCountImgOfPostCommand = """
        SELECT count(*)
	    FROM public."imageLinks"
        """
	    # where "postId" = %s

    # updatePostCommand = """
    #    UPDATE public.posts
    #     SET "isForRenter"=%s,price=%s,phone=%s,"timeStamp"=%s,district=%s,lng=%s,lat=%s,"isNeedToCheck"=%s
    #     WHERE id=%s
    #     """

    updatePostCommand = """
       UPDATE public.posts
        SET "timeStamp"=%s
        WHERE id=%s
        """

    updateCommentCommand = """
       UPDATE public.comments
        SET time=%s
        WHERE id=%s
        """
    
    cursor.execute(selectCommentCommand)
    post = cursor.fetchall()
    sumPost= len(post)
    print(sumPost)


    count = 0
    countSuccess = 0
    countFailure = 0
    countPostDelete = 0
    for postItem in post:

        count = count + 1
        print("count: ", count, "/", sumPost)
        try:
            id = postItem[0]
            print("comment: ", id)

            rawtimeStamp = str(postItem[1])
            createdAt = str(postItem[2])
            print ("rawtimeStamp: ", rawtimeStamp)
            print ("createdAt: ", createdAt)

            timeStamp = formatTimeCreatePost(createdAt, rawtimeStamp)

            print ("new timestamp: ", timeStamp)
            cursor.execute(updateCommentCommand, (timeStamp, id))

            connection.commit()
            countSuccess = countSuccess + 1
        except Exception as e:
            print("ERROR*: ", e)
            countFailure = countFailure + 1
            json.dump("ERROR POST: "+ str(e), f, ensure_ascii=False, indent=3)

    # cursor.execute(selectPostCommand)
    # post = cursor.fetchall()
    # sumPost= len(post)
    # print(sumPost)


    # count = 0
    # countSuccess = 0
    # countFailure = 0
    # countPostDelete = 0
    # for postItem in post:

    #     count = count + 1
    #     print("count: ", count, "/", sumPost)
    #     try:
    #         id = postItem[0]
    #         print("postId: ", id)
    #         content = postItem[1]

    #         with open('output-test.txt', 'a', encoding='utf-8') as f:                
    #             json.dump("=================================================", f, ensure_ascii=False, indent=3)
    #             json.dump("ID = "+ str(id) + "****", f, ensure_ascii=False, indent=3)
    #             json.dump(content, f, ensure_ascii=False, indent=3)

    #             if content == "":
    #                 cursor.execute(deletePostCommand, (id, ))
    #                 countPostDelete+=1
    #                 print("Delete post id ", id )
    #                 json.dump("DELETED POST", f, ensure_ascii=False, indent=3)

    #             else:
    #                 rawtimeStamp = str(postItem[3])
    #                 createdAt = str(postItem[4])
    #                 print ("rawtimeStamp: ", postItem[3])
    #                 print ("createdAt: ", postItem[4])

    #                 timeStamp = formatTimeCreatePost(createdAt, rawtimeStamp)

    #                 print ("new timestamp: ", timeStamp)

    #                 # # check isForRent base on content
    #                 # content = unicodedata.normalize('NFKC', content)
                    
    #                 # price = detectPrice(content)
    #                 # print ("********* PRICE: ", price)

    #                 # encodedContent = unicodedata.normalize('NFD', content).encode('ascii', 'ignore') # bo dau tieng Viet
    #                 # encodedContent = encodedContent.decode('ISO-8859-1')

    #                 # phone  = detectPhone(encodedContent)
                    
    #                 # # get img of post
    #                 # cursor.execute(selectCountImgOfPostCommand, (id, ))
    #                 # countImg = cursor.fetchone()[0]
    #                 # print("cout img post: ", countImg)

    #                 # # isNeedToCheck = False
    #                 # checkIsForRenterResult = checkIsForRenter(encodedContent, phone != "", countImg)
    #                 # isForRenter = checkIsForRenterResult['isForRenter']
    #                 # isNeedToCheck = checkIsForRenterResult['isNeedToCheck']
    #                 # print ("********* IS FOR RENTER: ", isForRenter)
    #                 # print ("********* IS NEED TO CHECK: ", isNeedToCheck)
                    
    #                 # district = detectDistrict({}, content, encodedContent)
    #                 # print ("********* DISTRICT: ", district)

    #                 # address = detectAddress(content)
    #                 # address = address + ' ' + district + ' Ho Chi Minh, Viet Nam'

    #                 # print ("*********ADDRESS: ", address)

                    
    #                 # try:
    #                 #     # get lng lat from address
    #                 #     lat = 10.746903
    #                 #     lng = 106.676292
    #                 #     geolocator = Nominatim(user_agent="buzzhome")
    #                 #     geoFromLocation = geolocator.geocode(address)

    #                 #     if not district:
    #                 #         district =  reFormatAddress(geoFromLocation.address)
                                    
    #                 #     lat = geoFromLocation.latitude
    #                 #     lng = geoFromLocation.longitude
    #                 # except Exception as e:
    #                 #     lat = 10.746903
    #                 #     lng = 106.676292
    #                 # print("Latitude : ", lat, "Longitude: ", lng)

    #                 # cursor.execute(updatePostCommand, (isForRenter, price, phone, timeStamp, district, lng, lat, isNeedToCheck, id))
    #                 cursor.execute(updatePostCommand, (timeStamp, id))

    #                 json.dump("UPDATED POST: price: " +" - timestamp: " + str(timeStamp), f, ensure_ascii=False, indent=3)

    #             connection.commit()
    #             countSuccess = countSuccess + 1
    #     except Exception as e:
    #         print("ERROR*: ", e)
    #         countFailure = countFailure + 1
    #         json.dump("ERROR POST: "+ str(e), f, ensure_ascii=False, indent=3)

    # connection.commit()

except (Exception, psycopg2.Error) as error:
    print("Error: ", error)
finally:
    print("RESULT: sum = ", sumPost, ", success = ", countSuccess, ", failure = ", countFailure)
    # closing database connection.
    if(connection):
        cursor.close()
        connection.commit()
        connection.close()
        print("PostgreSQL connection is closed")