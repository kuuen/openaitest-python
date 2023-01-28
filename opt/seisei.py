import os, argparse
import openai
import json
import socket
import logging
import bleach


#ロガーの生成
logger = logging.getLogger('mylog')
#出力レベルの設定
logger.setLevel(logging.INFO)
#ハンドラの生成
handler = logging.FileHandler('log/log.log')
#ロガーにハンドラを登録
logger.addHandler(handler)
#フォーマッタの生成
fmt = logging.Formatter('%(asctime)s %(message)s')

handler.setFormatter(fmt)

json_open = open('conf.json', 'r')
json_load = json.load(json_open)

# APIキーを設定
openai.api_key = json_load["api-key"]

#モデルを指定
model_engine = "text-davinci-003"


def generete(nyuuryoku):


  prompt = nyuuryoku

  response = openai.Completion.create(
      engine=model_engine,
      prompt=prompt,
      max_tokens=1024,
      n=1,
      stop=None,
      temperature=0.5,
  )

  texts = ''.join([choice['text'] for choice in response.choices])
  # print(texts)


  print('返答')
  print(texts)

  return texts


# 受信IP（外部からの接続は127.0.0.1では、多分ＮＧかと、、）
RCV_HOST = "0.0.0.0"
# 受信ポート
RCV_PORT = 4922
# 受信可能数（処理中に同時受信数が指定を超えると、待ちが発生せずに処理終了？？）
BACKLOG = 10
# 一度の通信受信できる最大データバイト数
BUFSIZE = 1024

print("start")

# ソケット定義
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sct:
    # 再使用設定(３つ目の引数が、考え方間違っているかも)
    sct.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, BUFSIZE)
    # 受信設定
    sct.bind((RCV_HOST, RCV_PORT))
    sct.listen(BACKLOG)

    # 継続受信のため、永久ループ
    while True:
        # クライアントの接続受付
        sock_cl, addr = sct.accept()

        logger.info('受付')
        print('受付')

        # ソケットから byte 形式でデータ受信
        data = sock_cl.recv(2048)
        # print(data.decode("utf-8"))

        try :
            a = json.loads(data.decode("utf-8"))
            print(a)
        except UnicodeDecodeError : 
            re = {
                "msg" : 'よくわからなかった。',
                "item" : ''
            }
            sock_cl.send(json.dumps(re).encode('utf-8'))
            sock_cl.close()
            continue
        except json.decoder.JSONDecodeError:
            re = {
                "msg" : 'よくわからなかった。',
                "item" : ''
            }
            sock_cl.send(json.dumps(re).encode('utf-8'))
            sock_cl.close()
            continue

        result = generete(a['msg'])

        re = {
            "msg" : result
        }

        # sock_cl.send(result.encode('utf-8'))
        sock_cl.send(json.dumps(re).encode('utf-8'))

        # クライアントのソケットを閉じる
        sock_cl.close()