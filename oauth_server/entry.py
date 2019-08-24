# -*- coding:utf-8 -*-

import json
import time

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.httpclient

import config
import local_db
import encrypt


g_db_path = "./data/db"
g_db = local_db.LocalDb(g_db_path)
g_db.write_dict(config.application_credentials)
g_des = encrypt.DesHelper("des_key_")

AUTHORIZE_CODE_EXPIRED = 3600
TOKEN_EXPIRED = 3600

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("oauth server running...")


@tornado.gen.coroutine
def verify_login_ticket(login_ticket):
    http_client = tornado.httpclient.AsyncHTTPClient()
    headers = {"cookie": "login_ticket=%s;" % login_ticket}
    url = "http://localhost:8888/is_login"
    response = yield http_client.fetch(url, headers=headers)
    r = json.loads(response.body)
    if r.get("result") == 0:
        raise tornado.gen.Return(True)
    raise tornado.gen.Return(False)


class AuthorizeHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        appid = self.get_query_argument("appid")
        scopes_raw = self.get_query_argument("scopes", "openid")
        redirect_uri = self.get_query_argument("redirect_uri")
        response_type = self.get_query_argument("response_type")
        state = self.get_query_argument("state", "")
        if response_type != "code":
            return self.write('{"result":20001}')
        scopes = scopes_raw.split("|")
        # 校验第三方应用信息
        app_raw = g_db.get(appid)
        if not app_raw:
            return self.write('{"result":20002}')
        app = json.loads(app_raw)
        if not redirect_uri.startswith(app.get("redirect_uri")):
            return self.write('{"result":20003}')
        app_scopes = app.get("scopes", ["openid"])
        for request_scope in scopes:
            if request_scope not in app_scopes:
                return self.write('{"result":20004}')
        # 校验登陆态
        login_ticket = self.get_cookie("login_ticket")
        valid_login_ticket = yield verify_login_ticket(login_ticket)
        if not valid_login_ticket:
            return self.write('{"result":20005}')
        code_info = {
            "appid": appid,
            "scopes": scopes,
            "redirect_uri": redirect_uri,
            "expired_time": int(time.time()) + AUTHORIZE_CODE_EXPIRED,
        }
        code_raw = json.dumps(code_info)
        code = g_des.encrypt(code_raw)
        return self.redirect("%s?code=%s?state=%s" % (redirect_uri, code, state))



class TokenHandler(tornado.web.RequestHandler):
    def get(self):
        appid = self.get_query_argument("appid")
        appsecret = self.get_query_argument("appsecret")
        redirect_uri = self.get_query_argument("redirect_uri")
        code = self.get_query_argument("code")
        grant_type = self.get_query_argument("grant_type")
        if grant_type != "authorize_code":
           return self.write('{"result":20001}')
        # 校验code
        code_raw = g_des.decrypt(code)
        if not code_raw:
           return self.write('{"result":20006}')
        code_info = json.loads(code_raw)
        current_time = int(time.time())
        expired_time = code_info.get("expired_time")
        if current_time > expired_time:
            return self.write('{"result":20007}')
        if redirect_uri != code_info.get("redirect_uri"):
            return self.write('{"result":20008}')
        # 校验第三方应用
        app_raw = g_db.get(appid)
        if not app_raw:
            return self.write('{"result":20002}')
        app = json.loads(app_raw)
        if appsecret != app.get("appsecret"):
            return self.write('{"result":20009}')
        # 生成token
        token_info = {
            "appid": appid,
            "expired_time": current_time + TOKEN_EXPIRED,
        }
        token_raw = json.dumps(token_info)
        access_token = g_des.encrypt(token_raw)
        resp = {
            "access_token": access_token,
            "expires_in": TOKEN_EXPIRED,
            "token_type": "bearer",
        }
        self.write(json.dumps(resp))
        

class QueryAppHandler(tornado.web.RequestHandler):
    def get(self):
        appid = self.get_query_argument("appid")
        app_raw = g_db.get(appid)
        if not app_raw:
            return self.write('{"result":20002}')
        app = json.loads(app_raw)
        app.pop("appsecret")
        return self.write(json.dumps(app))


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/query_app", QueryAppHandler),
        (r"/authorize", AuthorizeHandler),
        (r"/token", TokenHandler),
    ])
    application.listen(8889)
    tornado.ioloop.IOLoop.current().start()
