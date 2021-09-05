import regex as re
import unicodedata
import json
from geopy.geocoders import Nominatim
import time
from datetime import datetime

MAX_PRICE = 2000000000 # 2 bilion ~ 2*10^8 (near max interger)


def formatPrice(price):
    try:
        rawPrice = price

        price = price.replace(",", "").replace(".", "").replace(" ", "").replace("price", "").replace(":", "")

        if price.find("vnd") != -1 or price.find("vnđ") != -1 or price.find("đ") != -1 or price.find("₫") != -1:
            print("case1")
            price = price.replace("vnd", "").replace("vnđ", "").replace("đ", "").replace("₫", "")
            if float(price) < 100: #14đ => 14tr
                print("case2")
                price = float(price) * 1000000
            elif float(price) < 1000: #800đ => 800k
                print("case3")
                price = float(price) * 1000
            else:
                price = price
        elif price.find("tr") != -1 or  price.find("million") != -1:
            print("case4")
            price = price.replace("tr", "").replace("million", "").replace("d", "") # case usd
            price = float(price) * 1000000
        elif price.find("$") != -1 or price.find("usd") != -1:
            print("case5")
            price = price.replace("$", "").replace("usd", "")
            price = float(price) * 23000 # Note: convert dollar to vnd
        
        # case: 13tr5, 1.6tr, ...
        numberCountInPrice = re.findall("\d{1}", rawPrice)
        print(numberCountInPrice)
        if (len(numberCountInPrice)) < 5 and ((rawPrice.find(".") != -1 or  rawPrice.find(",") != -1) or (re.search("\d(million|tr)\s?\d", rawPrice))):
            print("case6")
            price = float(price) / 10

        if price > MAX_PRICE:
            print("case7")
            price /= 1000
        return price
        
    except Exception as e:
        print("Error while get price: ", e)
        return 0

def detectPrice(content):
    content = content.lower()
    try:
        # get price
        price = 0
        # price has to have unit (# phone)
        pricePattern = {
                    "\₫\d*\s", # ₫800 
                    "\$\d{1,3},{0,1}.{0,1}\d*", # $600
                    "\d{1,3},{0,1}.{0,1}\d*\s*usd", # 600 usd
                    "price ?:? ?\d{1,3},{0,1}.{0,1}\d{1,3},{0,1}\.{0,1}000", # PRICE : 385 USD / month - 9 million 
                    
                    "\d{3},\d{3} ?₫", # 800,000₫
                    "\d{3}\.\d{3} ?₫", # 800.000₫

                    "\₫ ?d{3},\d{3}", # 800.000
                    "\₫ ?d{3}\.\d{3}", # 800,000

                    "\d{1,3},\d{3},\d{3} ?đ", # 1,000,000đ
                    "\d{1,3}\.\d{3}\.\d{3} ?đ", # 1.000.000đ

                    "\d{1,3},\d{3},\d{3} ?vnd", # 1,000,000vnd
                    "\d{1,3}\.\d{3}\.\d{3} ?vnd", # 1.000.000vnd

                    "\d{1,3},\d{3},\d{3} ?₫", # 1,000,000 
                    "\d{1,3}\.\d{3}\.\d{3} ?₫", # 1.000.000
                    
                    "₫ ?\d{1,3},\d{3},\d{3}", # 1,000,000 
                    "₫ ?\d{1,3}\.\d{3}\.\d{3}", # 1.000.000
                    
                    "\d{1,3},{0,1}\.{0,1}\d{0,3} ?tr\ ?\d{0,1}", #11 tr, 11tr5
                    "\d{1,3},{0,1}\.{0,1}\d{1,3} ?million" # 4.5 million -15 million Ho Chi Minh City, Vietnam
                }
        seperatePatternOperator = "|"

        priceRegex = seperatePatternOperator.join(pricePattern)
        
        priceRegexResult = re.search(priceRegex, content, re.IGNORECASE)
        price = priceRegexResult.group(0)
        print ("raw price: ", price)
        price = formatPrice(price)
        # print ("=============***Price: ", price)
        return price
    except Exception as e:
        print("Error while format price: ", e)
        return 0


def formatDistrict(self, location):
    location = location.lower()
    if  ("binh tan" or "bình tân") in location:
        return "Quận Bình Tân"
    if ("binh thanh" or "bình thạnh") in location:
        return "Quận Bình Thạnh"
    if "Vinhomes" in location:
        return "Quận Bình Thạnh"
    if ("go vap" or "gò vấp") in location:
        return "Quận Gò Vấp"
    if ("phu nhuan" or "phú nhuận") in location:
        return "Quận Phú Nhuận"
    if ("tan binh" or "tân bình") in location:
        return "Quận Tân Bình"
    if ("san bay" or "sân bay") in location:
        return "Quận Tân Bình"
    if ("tan phu" or "tân phú") in location:
        return "Quận Tân Phú"
    if ("thu duc" or "thủ đức") in location:
        return "Quận Thủ Đức"
    if ("binh chanh" or "bình chánh") in location:
        return "Huyện Bình Chánh"
    if ("can gio" or "cần giờ") in location:
        return "Huyện Cần Giờ"
    if ("cu chi" or "củ chi") in location:
        return "Huyện Củ Chi"
    if ("hoc mon" or "hóc môn") in location:
        return "Huyện Hóc Môn"
    if ("nha be" or "nhà bè") in location:
        return "Huyện Nhà Bè"
    if ("thao dien" or "thảo điền") in location:
        return "Quận 2"
    if ("millenium" or "gold view" or "goldview") in location:
        return "Quận 4"
    
    district =  re.search("\d", location)

    try: 
        district = district.group(0)
        return "Quận " + district
    except Exception as e: 
        print("Error while format loaction: ", e)
        return ""
    

def detectDistrict(self, content, encodedContent):
    encodedContent.lower()
    locationRegex1 = "(quan\s*|((?<!\w)q)\.?\s*|quận\s*|((?<!\w)q)\.?\s*|district\s+|dist.?\s+|((?<!\w)d)\B\.?\s*)(\d+)|(quan\s+|q\.?\s*)?(binh tan|binh thanh|go vap|phu nhuan|tan binh|tan phu|thu duc)|(quận\s+|q\.?\s*)?(bình tân|bình thạnh|gò vấp|phú nhuận|tân bình|tân phú|thủ đức)|(huyen\s+)?(binh chanh|can gio|cu chi|hoc mon|nha be)"
    locationRegexResult = re.search(locationRegex1, encodedContent, re.IGNORECASE)

    if locationRegexResult:
        try:
            location = locationRegexResult.group(0)
            print ("raw location: ", location)
            location = formatDistrict(self, location)
            return location
        except Exception as e:
            print("Error while get location: ", e)
            return ''
    else:
        print("District not found!")
        return ''


def reFormatAddress(address):
    # address = content
    # geolocator = Nominatim(user_agent="buzzhome")
    # location = geolocator.geocode(address)
    # address = location.address
    print('Address after get district 1: ', address)
    encodedContent = unicodedata.normalize('NFD', address).encode('ascii', 'ignore') # bo dau tieng Viet
    encodedContent = encodedContent.decode('ISO-8859-1')
    districtAfterDetect = detectDistrict({},'', encodedContent)
    print('Address after get district: ', districtAfterDetect)
    return districtAfterDetect


def detectAddress(content):
    content = content.lower()
    locationRegex = "(\w*\d+\w*\s?\/? ?\w*\d+\w*\s)*đường\s*(?!(hẻm|rộng|lớn|to|nhỏ|cao|nhựa|thông|dạo|chạy|đi))(\d+\/\d+|\d+|((\w+\s){1})*?(\p{Lu}\p{Ll}+\s*){2,4}(\p{N}\p{L}*)*|(\w+\s*){1,4})(,?\s*?(phường |xã |huyện |tỉnh )(\w+\s*){1,3}){0,3}|((?<=địa chỉ:)|(?<=address:)|(?<=location:)|(?<=add:)|(?<=địa chỉ :)|(?<=address :)|(?<=add :)|(?<=location :)|(?<=địa điểm :))(\s*\w+ ?,?)+|(\d+\/\d+|\d+|(\p{Lu}\p{Ll}+\s*){2,4}(\p{N}\p{L}*)*|(\w+\s*){1,4})(street|((?<!\w)str))|phú mỹ hưng|thảo điền|thao dien|vinhome|sân bay|san bay|masteri an phu|an phu|an phú|sun avenue|bến thành|ben thanh|làng đại học|lang dai hoc"
    locationRegexResult = re.search(locationRegex, content, re.IGNORECASE)

    if locationRegexResult:
        try:
            location = locationRegexResult.group(0)
            # location = formatDistrict(self, location)
            return location
        except Exception as e:
            print("Error while get location: ", e)
            return ''
    else:
        locationRegex2 = "(gần ?|tại ?|ở ?|khu vực ?|near ?|công viên ?|cong vien ?|chung cư ?| chung cu ?|liền kề ?|lien ke ?|cạnh ?|lân cận ?|khu đô thị ?|khu do thi ?|căn hộ ?|can ho ?|khu ?){1,5}\s*(\d+\s?-?\s?\d+)?\s*((\p{Lu}\p{Ll}+\s*?){1,*}|(\p{L}+\s*?){3})"
        
        print("using regex location 2")
        locationRegexResult = re.search(locationRegex2, content)
        try:
            location = locationRegexResult.group(0)
            # format: remove prefix words
            location = location.replace("gần", "").replace("tại", "").replace("ở", "").replace("khu vực", "").replace("near", "").replace("chung cư", "").replace("liền kề", "").replace("lien ke", "").replace("cạnh", "").replace("lân cận", "").replace("khu", "").replace("PMH", "Phú Mỹ Hưng").strip()
            # write to output file
            # print("**********ADDRESS FOUND: ", location )

            return location
        except Exception as e:
            print ("**********ADDRESS NOT FOUND: ", e)
            return ''


def checkIsForRenter(content, isHavePhone, imgCount): # content with ascii only (ex: chữ có dấu -> chu co dau)
    content = content.lower()
    # print("check is for renter: ", isHavePhone, imgCount, content)
    
    # filter isForRenter
    isForRenter = True # note: set as high priority
    isNeedToCheck = False
    if re.search("can thue|canthue|ngan sach|can tim thue|muon thue|muon tim|looking for|de thue|tim mua|tim thue|nhu cau thue|can tim|tim host|dang tim|tim can ho|tim nha|tim phong|khach tim|host co can phu hop|tim host|khach\s?\d*\s?can|de thue|tai chinh|co\s?\d*\s?khach|can\s?\d*\s?phong|can\s?\d*\s?can|can\s?\d*\s?nha|khach\s?\w*\s?can|khach\s?\w*\s?tim|co\s?\w*\d*\s?khach|requirement|client\s?\w*\s?need", content, re.IGNORECASE):
        if re.search("cho thue|chothue|for rent|forrent|housing for expats|lien he xem phong|duoc tu van|gia thue|hotline|gia phong|gia nha|giá chỉ|gia chi|lease|leasing|lien he xem nha|lien he xem phong|to support you|the rent is include|cam ket hinh that|available now|see more|for more info|available as|the rent include|con\s?\d*\s?phong|con\s?\d*\s?can|duoc tu van", content, re.IGNORECASE):
            # Note: not sure, need to check base on others attribute (img | phone)
            if isHavePhone | imgCount > 0:
                isForRenter = True
                isNeedToCheck = True
            else:
                isForRenter = False
        elif len(content) > 300 and imgCount > 1 and isHavePhone: # length, img (>=2), have phone
            isForRenter = True
            isNeedToCheck = True
        else:
            isForRenter = False
    else:
        isForRenter = True

    rs = {'isForRenter': isForRenter, 'isNeedToCheck': isNeedToCheck }
    return rs


def detectPhone(content): # content with ascii only (ex: chữ có dấu -> chu co dau)
    content = content.lower()
    phoneRegex = "(?<!\d)(\(\+84\)|\(84\)|84|\+84|0)(\d|\.|\s|\,|\-){8,12}\d"
    phoneRegexResult = re.search(phoneRegex, content, re.IGNORECASE)

    try:
        phone = phoneRegexResult.group(0)
        # format phone
        
        print ("**********PHONE: ", phone)
        return phone
    except Exception as e:
        print("Do not have phone in post: ", e)
        return ''


# convert time get from fb post to time stamp (3 case) (Ex for input: 26 September at 15:40 | 2 minutes | 2 hrs| now)
def formatTimeCreatePost(createdTimeStamp, timeCreatePost):
    createdTimeStamp = str(createdTimeStamp)
    timeCreatePost = str(timeCreatePost)
    # print("start format time: ", createdTimeStamp, timeCreatePost)
    try:
        lastIndex = createdTimeStamp.find('.')
        if lastIndex == -1:
            lastIndex = len(createdTimeStamp)

        formatTime = createdTimeStamp[0 : lastIndex] + " UTC"

        # timeStampCreatedAt = time.mktime(datetime.strptime(formatTime,  "%Y-%m-%d %H:%M:%S %Z").timetuple())
        timeStampCreatedAt = time.mktime(time.strptime(formatTime, "%Y-%m-%d %H:%M:%S %Z"))
        rs = 0
        try:
            numberTime = float(re.search("\d*", timeCreatePost).group(0))
        except:
            numberTime = 0

        if timeCreatePost.find('mi') != -1:
            rs = timeStampCreatedAt + numberTime * 60     
        elif timeCreatePost.find('hr') != -1:
            rs = timeStampCreatedAt + numberTime * 60 * 60    
        elif timeCreatePost.find('now') != -1:
            rs = timeStampCreatedAt
        elif timeCreatePost.find('Yesterday') != -1:
            date = createdTimeStamp[0:10]

            if (timeCreatePost.find('AM') != -1):
                timeString = timeCreatePost[9:17] # ex ' at 07:10'
                rs = time.mktime(time.strptime(date + timeString, '%Y-%m-%d at %H:%M')) - 24 * 60 * 60
            elif (timeCreatePost.find('PM') != -1):
                timeString = timeCreatePost[9:17] # ex ' at 07:10'
                rs = time.mktime(time.strptime(date + timeString, '%Y-%m-%d at %H:%M')) - ( 24 + 12) * 60 * 60
            else:
                timeString = timeCreatePost[9:18] # ex ' at 07:10'
                rs = time.mktime(time.strptime(date + timeString, '%Y-%m-%d at %H:%M')) - 24 * 60 * 60
        else:
            rs = convertTimeStringCreatePostToTimeStamp(timeCreatePost)

        dt_object = datetime.fromtimestamp(rs)
        print("timeStamp after format =", dt_object)
        return dt_object
    except Exception as e:
        print("Error when format time: ", e)
        return timeCreatePost


# convert time get from fb post to time stamp (Ex for input: 26 September at 15:40)
def convertTimeStringCreatePostToTimeStamp(rawTimeStamp):
    rawTimeStamp = '2020 ' + rawTimeStamp
    rs = time.mktime(time.strptime(rawTimeStamp, '%Y %d %B at %H:%M'))
    return rs

