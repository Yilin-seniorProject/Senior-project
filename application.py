import sqlite3
import googlemaps
from ast import literal_eval
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, LocationSendMessage

gmaps = googlemaps.Client(key='AIzaSyDCRc7BNieQSBcle_1GdCC0QrqVg61EC_8')

app = Flask(__name__)

line_bot_api = LineBotApi('fxk7TqJ720eS26A+yzGorr8KmJhwiJnBK1sR1ugM53qNhvGegYYBl7p4GGeinqVEAewlGO3PuSk7966ijSmdxMnOlv7sOkjD+2fRFd5ck+T7iFEtqy9zZBrhJUBcV325WKKBRnmMTp54JregWJmGgAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('105a46a47e7c126f30f26bf34aedf239')

# 連接 Linebot
@app.route("/callback", methods=['POST', 'GET'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# Linebot 回應處理
@handler.add(MessageEvent)
def handleMessage(event):
    try:
        line_bot_api.reply_message(event.reply_token, LocationSendMessage(title="國立中央大學",
                                                                          address="320桃園市中壢區中大路300號",
                                                                          latitude=24.96819583394539,
                                                                          longitude= 121.19527384809079,))
    except Exception as e:
        print(e)
    
    return

# INSERT data to db
@app.route("/dataCollector", methods=['POST'])
def feedback():
    geo =  literal_eval(request.files["json"].stream.read().decode('utf-8'))['Geo']
    file = request.files["file"].stream.read()
    fileName = request.files["file"].filename.split('.')[0]
    with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO point(`ImageName`,`ImageData`,`Latitude`,`Longitude`) VALUES(?,?,?,?)", (fileName, file, geo[0], geo[1]))
            con.commit()
            cur.close()
    return 'OK'

        

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)