## Prerequisite
You have to run this Crawler on Python with version 3.x. (recomment 3.9.6)

## Pre-running
Before running the Facebook Group Crawler, there are some pre-step codes need doing first in terminal (MacOS) or cmd (Windows):
* cd buzzhome-crawler
* python -m pip install -r dependencies.txt
* Create a new file in the same folder and name it "taikhoan.txt"
* Open the created file and input your Facebook cookies account (F12 => tab Application => Cookies) with the following format: fr,xs,c_user,datr,sb => Save it
* Open dataToDb.py => Edit your database information => Save it

## Run the Crawler
* cd buzzhome-crawler
* python dataToDb.py

**Note:** 
* You can set up the depth of crawling by searching for the command "*fb = facebook(depth=yourDepth)*" in dataToDb.py, and set the depth to your desire.
