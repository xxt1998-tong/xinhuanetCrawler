# 导入模板模块
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from xinhuanetCrawler import xinhuanet_crawl_text
from xinhuanet_pic import xinhuanet_crawl_pic
from xinhuanet_video import xinhuanet_crawl_video

# Flask相关变量声明
app = Flask(__name__)

app.config.update(
    DEBUG=True
)
# 跨域问题
CORS(app, supports_credentials=True)


@app.route('/xinhuanet', methods=["post", "get"])
def xinhuanet():
    # keys = request.form.get("key")  # 调用者传参 ky
    # 请求进来 输入爬取内容
    # taobao_details.get_detail(keys)#这里就是你的爬虫程序接入口
    # 爬虫程序
    key = request.values.get('key')
    x1 = xinhuanet_crawl_text()
    x2 = xinhuanet_crawl_pic()
    x3 = xinhuanet_crawl_video()
    return "xinhuanet_ok"  # jsonify({"code": 1})


if __name__ == '__main__':
    app.run(port=5555, debug=True, host='127.0.0.1')
    http_server = WSGIServer(('127.0.0.1', 5555), app, handler_class=WebSocketHandler)
    http_server.serve_forever()

# import requests
# import flask
# from flask import request
#
# server = flask.Flask(__name__)
#
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
#                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
#
#
# @server.route('/', methods=['get', 'post'])
# def reg():
#     funItemMenuId = request.values.get('funItemMenuId')  # 设置参数
#     position = request.values.get('position')
#     # 自己定义url,这里隐藏了部分url，但功能是一样的
#     url = 'funItemMenuId={0}&position={1}.format(funItemMenuId, position)
#     r = requests.get(url, headers=headers)
#     return r.text
