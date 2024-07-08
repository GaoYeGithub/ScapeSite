from requests.exceptions import ConnectionError
import requests, time, os, smtplib, replit, schedule
from bs4 import BeautifulSoup
from replit import db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
import requests

def getHub():
    url = "https://replit.com/bounties"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    bounty_links = soup.find_all("a", {"class": "css-1om7s53"})

    if bounty_links:
      print(bounty_links)
    else:
      print("No bounty links found on the page.")


def addToDB():
  link = input("Link: ")
  price = float(input("Price: "))
  db[time.time()] = {"link": link, "price" : None, "level": price}

def emailMe(level, price, link):
  password = os.environ['mailPassword']
  username = os.environ['mailUsername']
  host = "smtp.gmail.com"
  port = 587
  s = smtplib.SMTP(host=host, port=port)
  s.starttls()
  s.login(username, password)

  msg = MIMEMultipart()
  msg["To"] = username
  msg["From"] = username
  msg["Subject"] = "Product is Cheaper!"
  text = f"""<p><a href='{link}'>This item</a> is now {price} which is below your purchase level of {level}</p>"""
  msg.attach(MIMEText(text, 'html'))
  s.send_message(msg)
  del msg
    
def update():
  keys = db.keys()
  for key in keys:
    url = db[key]["link"]
    price = db[key]["price"]
    level = db[key]["level"]
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    myPrice = soup.find_all("span", {"class": "price"})

    thisPrice = float(myPrice[0].text[1:].replace(",",""))

    if thisPrice != price:
      db[key]["price"] = thisPrice
      if thisPrice <= level:
        print("Cheaper")
        emailMe(level, price, url)


website = input("Don't put (http:// or https://) just the link>")
print()
if "http://" not in website:
    website = ''.join(("http://", website))
print(website)
time.sleep(2)
try:
    page = requests.get(website)
except ConnectionError:
    print()
    print("The website you entered does not exist.")
else:
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find('title')
    print()
    print("The title of %s is %s." % (website, title))
    time.sleep(4)
    print()
    setContinue = input("Would you like to scrape the rest of this page?").lower()
    if setContinue == "yes" :
        print()
        print("Creating your scraped page...")
        time.sleep(5)
        print()
        replit.clear()
        print(soup)



schedule.every(1).day.do(update)
update()
while True:
  schedule.run_pending()
  time.sleep(1)
  getHub()
