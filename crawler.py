from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import argparse
import csv
import json
import io
from datetime import datetime
import re
from geopy.geocoders import Nominatim
import unicodedata
from functionUtils import *

chrome_options = Options()
chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# chrome_options.add_argument("--headless")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--incognito")

fbUrl = "https://m.facebook.com"


class facebook:
    def __init__(self, depth=1):
        self.fbUrl = "https://m.facebook.com"
        self.depth = depth
        with open('taikhoan.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self.fr = row[0]
                self.xs = row[1]
                self.c_user = row[2]
                self.datr = row[3]
                self.sb = row[4]
        self.driver = webdriver.Chrome(
            options=chrome_options, executable_path="chromedriver.exe")
        self.content = dict()  # content of post

    def login(self):
        self.driver.get(self.fbUrl)
        time.sleep(1)
        # userEle = self.driver.find_element_by_css_selector('#email')
        # userEle.send_keys('chukhanh1998@gmail.com')
        # time.sleep(1)
        # passEle = self.driver.find_element_by_css_selector('#pass')
        # passEle.send_keys('Khanh020798@2')
        # time.sleep(3)
        # loginEle = self.driver.find_element_by_css_selector('#u_0_b')
        # loginEle.click()
        # time.sleep(1)

        self.driver.add_cookie({'name': 'fr', 'value': self.fr})
        self.driver.add_cookie({'name': 'xs', 'value': self.xs})
        self.driver.add_cookie({'name': 'c_user', 'value': self.c_user})
        self.driver.add_cookie({'name': 'datr', 'value': self.datr})
        self.driver.add_cookie({'name': 'sb', 'value': self.sb})
        self.driver.get(self.fbUrl)
        time.sleep(4)

    def verifyLogin(self):
        try:
            self.driver.find_element_by_css_selector('#email')
            return False
        except:  # NoSuchElementException
            return True

    def group(self, group, isTest):
        try:
            # print("Crawling group: ", group)
            self.driver.get('https://m.facebook.com/groups/' + group + '/')
            time.sleep(3)
            # scroll down for more posts
            if not isTest:
                for scroll in range(self.depth):
                    self.driver.execute_script(
                        "window.scrollTo(0,document.body.scrollHeight);")
                    time.sleep(2)

            # Get wrapper of all post and save them to an array named posts
            posts = self.driver.find_elements_by_class_name("story_body_container")
            time.sleep(1)
            flag = 0
            linkDetail = []
            # get all link to post detail
            if not isTest:
                for ind, postItem in enumerate(posts):
                    if flag >= 5:
                        break
                    wrap = postItem.find_element_by_css_selector(
                        "div[data-sigil='m-feed-voice-subtitle']")
                    tagLink = wrap.find_element_by_tag_name("a")
                    href = tagLink.get_attribute("href")
                    linkDetail.append(href)
                    flag = flag + 1

            if isTest:
                linkDetail.append(
                    'https://m.facebook.com/groups/housing.apartment.saigon.vietnam/permalink/688365555197665/')
                # linkDetail.append('https://m.facebook.com/groups/457452884613043/permalink/1288429404848716')
                # linkDetail.append('https://m.facebook.com/groups/21620976623/permalink/10158618891666624')
                # linkDetail.append('https://m.facebook.com/groups/21620976623?view=permalink&id=10158633712661624')

            # go to post detail
            for ind, postLink in enumerate(linkDetail):
                try:
                    # shorten post link
                    endIndexPostLink = postLink.find("&refid")
                    if endIndexPostLink > 0:
                        postLink = postLink[0:endIndexPostLink]

                    print("Get post detail: ", postLink)
                    self.driver.get(postLink)
                    time.sleep(3)
                    # check shared post
                    h3 = self.driver.find_elements_by_tag_name('h3')
                    linkInTitle = h3[0].find_elements_by_tag_name('a')
                    # real post, not shared post
                    if (len(linkInTitle) == 2):
                        # get post's time
                        time_element = self.driver.find_element_by_css_selector(
                            "abbr")  # get tag abbr of time posting
                        utime = time_element.text
                        currentTime = datetime.now()
                        timeStamp = formatTimeCreatePost(currentTime, utime)
                        # print ("timeStamp: ", timeStamp)


                        time_element.click()
                        time.sleep(3)
                        print("after click to post")

                        # get post element again
                        post = self.driver.find_element_by_class_name(
                            "story_body_container")

                        avatarOfUser = ""
                        nameOfUserPost = ""
                        profileOfUserPost = ""
                        try:
                            # get avatar user of post
                            avatarOfUserPostEle = post.find_element_by_tag_name(
                                "i")
                            avatar = avatarOfUserPostEle.get_attribute("style")
                            avatarOfUser = avatar[avatar.find(
                                "url") + 5: avatar.find('")')]

                            print("Avatar of User Post: ", avatarOfUser)
                            # get name user of post
                            nameOfUserPostEle = post.find_element_by_css_selector("h3[class='_52jd _52jb _52jh _5qc3 _4vc- _3rc4 _4vc-']").find_element_by_tag_name(
                                "span").find_element_by_tag_name("strong").find_element_by_tag_name("a")
                            nameOfUserPost = nameOfUserPostEle.text
                            print("Name of User Post: ", nameOfUserPost)

                            profileOfUserPost = nameOfUserPostEle.get_attribute(
                                "href")
                            print("Profile of User Post: ", profileOfUserPost)

                        except Exception as e:
                            print("Error! Cannot get user info: ", e)


                        # get post's content: multim cases (get text normally | get text inside background img | post with imgs | post without imgs)
                        text = ''
                        try:
                            try:
                                # text with img
                                text = post.find_element_by_css_selector(
                                    "div[class='_4gur _5t8z']").text
                                print("content in post with img div: ", text)
                                
                            except:
                                try:
                                    # text without img
                                    text = post.find_element_by_css_selector(
                                        "div[class='_5rgt _5nk5']").text
                                    print("content in post without img: ", text)
                                    
                                except:
                                    # get text inside background img
                                    text = self.driver.find_element_by_class_name(
                                        '_2z79').find_element_by_tag_name("span").text
                                    print("content in bg: ", text)
                                    
                                        
                        except Exception as e:  
                            text = self.driver.find_element_by_class_name(
                                '_3w8y').text
                            print("content in special case: ", text)

                        print(text)

                        if (("căn" in text.lower()) or ("nhà" in text.lower()) or ("phòng" in text.lower()) or ("chung cư" in text.lower()) or ("căn hộ" in text.lower()) or ("khách sạn" in text.lower()) or ("PN" in text.lower()) or ("đất" in text.lower()) or ("apartment" in text.lower()) or ("house" in text.lower()) or ("real estate" in text.lower()) or ("homestay" in text.lower()) or ("villa" in text.lower())):
                            print("Có nội dung bds")
                        else:
                            print("không có nội dung bds")
                            break

                        # get all image links
                        print("Before get img")
                        imageLinksEle = post.find_elements_by_tag_name('a')
                        isHaveImg = False
                        linkToImg = ""
                        images = []

                        
                        # find first img element
                        for ele in imageLinksEle:
                            href = ele.get_attribute("href")
                            # case multi img
                            if href and href.__contains__('/photos/viewer/'):
                                linkToImg = href
                                print('Found raw link to img ', linkToImg)
                                isHaveImg = True
                                break
                        time.sleep(2)

                        try:
                            if isHaveImg:
                                fbid = linkToImg[linkToImg.find(
                                    "photo=") + 6: linkToImg.find("&profileid")]
                                print("fbid: ", fbid)
                                pcb = linkToImg[linkToImg.find(
                                    "pcb.") + 4: linkToImg.find("&photo=")]
                                print("pcb: ", pcb)

                                linkToImg = 'https://www.facebook.com/photo?fbid=' + fbid + '&set=pcb.' + pcb
                                self.driver.get(linkToImg)
                                self.driver.add_cookie(
                                    {'name': 'c_user', 'value': self.c_user})
                                self.driver.add_cookie(
                                    {'name': 'xs', 'value': self.xs})

                                self.driver.get(linkToImg)
                                print("link to img: ", linkToImg)
                                time.sleep(6)

                                #catch in case this is video
                                try:
                                    mediaPreviewEle = self.driver.find_element_by_css_selector(
                                        "div[data-pagelet='MediaViewerPhoto']")
                                    imgEle = mediaPreviewEle.find_element_by_tag_name(
                                        'img')
                                    images.append(imgEle.get_attribute("src"))
                                    print(images[len(images)-1])
                                except Exception as e:
                                    print("This is not img: ", e)

                                nextBtn = self.driver.find_element_by_css_selector(
                                    "div[aria-label='Next photo']")

                                for img in range(len(imageLinksEle)):
                                    nextBtn.click()
                                    time.sleep(3)

                                    try:  # catch in case this is video
                                        mediaPreviewEle = self.driver.find_element_by_css_selector(
                                            "div[data-pagelet='MediaViewerPhoto']")
                                        print("got preview element")
                                        imgEle = mediaPreviewEle.find_element_by_tag_name(
                                            'img')
                                        images.append(imgEle.get_attribute("src"))
                                    except Exception as e:
                                        print("This is not img: ", e)

                                    print(images[len(images)-1])
                                    nextBtn = self.driver.find_element_by_css_selector(
                                        "div[aria-label='Next photo']")

                                print("imgs length: ", len(images))
                        except Exception as e:
                            print("Warning! Cannot get images: ", e)

                        # case not have img
                        if len(images) < 1:
                            print("Post no img", len(images))
                            for ele in imageLinksEle:
                                href = ele.get_attribute("href")
                                # case multi img
                                if href and href.__contains__('/photo.php?'):
                                    linkToImg = href
                                    print('Found raw link to img ', linkToImg)
                                    try:
                                        fbid = linkToImg[linkToImg.find(
                                            "fbid=") + 5: linkToImg.find("&id=")]
                                        print("fbid: ", fbid)
                                        pcb = linkToImg[linkToImg.find(
                                            "set=gm.") + 7: linkToImg.find("&source=")]
                                        print("pcb: ", pcb)

                                        linkToImg = 'https://www.facebook.com/photo?fbid=' + fbid + '&set=pcb.' + pcb
                                        self.driver.get(linkToImg)
                                        self.driver.add_cookie(
                                            {'name': 'c_user', 'value': self.c_user})
                                        self.driver.add_cookie(
                                            {'name': 'xs', 'value': self.xs})

                                        self.driver.get(linkToImg)
                                        print("link to img: ", linkToImg)
                                        time.sleep(6)

                                        mediaPreviewEle = self.driver.find_element_by_css_selector(
                                            "div[data-pagelet='MediaViewerPhoto']")
                                        imgEle = mediaPreviewEle.find_element_by_tag_name(
                                            'img')
                                        images.append(imgEle.get_attribute("src"))
                                        isHaveImg = True
                                        print(images[len(images)-1])
                                    except Exception as e:
                                        print("Warning! Cannot get images: ", e)
                                    break

                        
                        # check isForRent base on content
                        # normalize content (bold, italic, .... => normal text)
                        content = unicodedata.normalize('NFKC', text)
                        
                        price = detectPrice(content)
                        print ("********* PRICE: ", price)

                        # bo dau tieng Viet
                        encodedContent = unicodedata.normalize('NFD', content).encode('ascii', 'ignore') 
                        encodedContent = encodedContent.decode('ISO-8859-1')

                        phone  = detectPhone(encodedContent)
                        
                        checkIsForRenterResult = checkIsForRenter(encodedContent, phone != "", len(images))
                        isForRenter = checkIsForRenterResult['isForRenter']
                        isNeedToCheck = checkIsForRenterResult['isNeedToCheck']
                        print ("********* IS FOR RENTER: ", isForRenter)
                        print ("********* IS NEED TO CHECK: ", isNeedToCheck)
                        
                        district = detectDistrict(self, content, encodedContent)
                        print ("********* DISTRICT: ", district)

                        # accurate address (street, ward, ...)  
                        address = detectAddress(content)
                        address = address + ' ' + district + ' Ho Chi Minh, Viet Nam'
                        print ("*********ADDRESS: ", address)
                        
                        # get lng lat from address
                        lat = 10.746903
                        lng = 106.676292
                        try:
                            geolocator = Nominatim(user_agent="buzzhome")
                            geoFromLocation = geolocator.geocode(address)
                            print("Address: ", address)
                            if not district:
                                district =  reFormatAddress(geoFromLocation.address)
                                
                            lat = geoFromLocation.latitude
                            lng = geoFromLocation.longitude
                        except Exception as e:
                            lat = 10.746903
                            lng = 106.676292
                        print("Latitude : ", lat, "Longitude: ", lng)


                        postcontent = {"timeStamp": timeStamp, "content": text, "link": images, "postLink": postLink, "groupId": group, "username": nameOfUserPost, "userAvatar":  avatarOfUser, "userProfileLink": profileOfUserPost, "isForRenter": isForRenter, "price": price, "district": district, "address": address, "lat": lat, "lng": lng, "phone": phone, "isNeedToCheck": isNeedToCheck}

                        self.content[ind] = postcontent
                        # print("Content: ", self.content[ind])
                        time.sleep(1)
                except Exception as e:
                    print("Error while getting post detail ", e)

            self.content = {k: v for k, v in sorted(
                self.content.items(), key=lambda item: item[1]["timeStamp"])}
        except Exception as e:
            print("Error while group ", e)

    def write2File(self, fileName):
        try:
            currentTime = datetime.now()
            with open(fileName, 'a', encoding='utf-8') as f:
                json.dump(str(currentTime), f, ensure_ascii=False, indent=3)
                json.dump(self.content, f, ensure_ascii=False, indent=4)
        except Exception as e:
                print("Error while read post from db ", e)

    def write2DBOnlyNew(self, cursor, connection):
        try:
            print("start writing to db")
            currentTime = datetime.now()

            insertPostCommand = """
            insert into posts("timeStamp","content", "groupId", "postLink", "username", "userAvatar", "userProfileLink", "lng", "lat", "isForRenter", "price", "district", "address", "phone", "isNeedToCheck","createdAt", "updatedAt") values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id; 
            """

            updatePostCommand = """
            UPDATE posts
            SET content=%s, "timeStamp"=%s
            WHERE id=%s;
            """

            insertImageCommand = """
            insert into "imageLinks"("postId","link","createdAt", "updatedAt") values (%s,%s,%s,%s);
            """

            selectPostByLinkCommand = """
            SELECT id, content, "timeStamp" FROM posts WHERE "postLink"=%s
            """

            for ind, post in self.content.items():
                print(post["content"])
                cursor.execute(selectPostByLinkCommand, (post["postLink"],))
                duplicatedPost = cursor.fetchone()
                isDuplicated = False

                if duplicatedPost:
                    isDuplicated = True
                    postid = duplicatedPost[0]
                    print("duplicated post, ", postid)

                    # update only if content or timeStamp changed
                    if (post["content"] != duplicatedPost[1]) or (post["timeStamp"] != duplicatedPost[2]):
                        print('Post changed, go to update')
                        cursor.execute(updatePostCommand,
                                    (post["content"], post["timeStamp"], postid))
                    else:
                        print('Post is not changed, not update')
                else:
                    print("New post, go to insert: ", post["postLink"])
                    cursor.execute(insertPostCommand,
                                (post["timeStamp"], post["content"], post["groupId"], post["postLink"], post["username"], post["userAvatar"], post["userProfileLink"], post["lng"], post["lat"], post["isForRenter"], post["price"], post["district"], post["address"], post["phone"], post["isNeedToCheck"], currentTime, currentTime))
                    postid = cursor.fetchone()[0]
                    print("inserted post: ", postid)

                    # Note: not update img, just create when insert post
                    for link in post["link"]:
                        cursor.execute(insertImageCommand, (str(
                            postid), link, currentTime, currentTime))
                    print("inserted img")

                connection.commit()

            print("finish writing to db")
        except Exception as e:
            print("Error while write2DBOnlyNew ", e)

if __name__ == '__main__':
    fb = facebook(depth=1)
    fb.login()
    if fb.verifyLogin():
        print("login successful")
    else:
        print("login failed")
        exit()
    fb.group("950713841719944")
    print(fb.content)
    fb.write2File('out.txt')
    # fb.driver.get"https://www.facebook.com/groups/950713841719944/")
    time.sleep(5)
    fb.driver.close()
