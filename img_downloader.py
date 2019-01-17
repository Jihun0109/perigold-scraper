import requests
import shutil

url = "https://secure.img1-fg.wfcdn.com/im/70792572/resize-h800%5Ecompr-r85/6523/65233886/Valentina+Velvet+Heart+Vanity+Tray.jpg"
url = "https://secure.img1-ag.wfcdn.com/im/93650840/resize-h800%5Ecompr-r85/6523/65233893/300+Piece+Shagreen+Poker+Set.jpg"

r = requests.get(url, stream=True)
if r.status_code == 200:
    with open("test.jpg", 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)