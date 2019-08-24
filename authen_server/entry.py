# -*- coding:utf-8 -*-

import json
import base64

import tornado.ioloop
import tornado.web

import config
import local_db


g_db_path = "./data/db"
g_db = local_db.LocalDb(g_db_path)
g_db.write_dict(config.users)


def generate_ticket(dic):
    dict_raw = json.dumps(dic)
    ticket_raw = base64.b64encode(dict_raw.encode("utf-8"))
    return ticket_raw


def decode_ticket(ticket_raw):
    dict_raw = base64.b64decode(ticket_raw)
    ticket = json.loads(dict_raw)
    return ticket


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class ListUsersHandler(tornado.web.RequestHandler):
    def get(self):
        users = {}
        names = g_db.keys()
        print(names)
        for name in names:
            users[name] = g_db.get(name)
        self.write(json.dumps(users))


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        username = self.get_query_argument("username")
        password = self.get_query_argument("password")
        expect_pwd = g_db.get(username)
        if password != expect_pwd:
            return self.write(json.dumps({"result": 10001}))
        session_dict = {"username":username, "password":password}
        self.set_secure_cookie("login_ticket", generate_ticket(session_dict))
        return self.write(json.dumps({"result": 0}))


class VerifyLoginHandler(tornado.web.RequestHandler):
    def get(self):
        login_ticket_raw = self.get_secure_cookie("login_ticket")
        if not login_ticket_raw:
            return self.write(json.dumps({"result": 10002}))
        login_ticket = decode_ticket(login_ticket_raw)
        if not login_ticket:
            return self.write(json.dumps({"result": 10003}))
        username = login_ticket.get("username")
        password = login_ticket.get("password")
        expect_pwd = g_db.get(username)
        if expect_pwd != password:
            return self.write(json.dumps({"result": 10004}))
        return self.write(json.dumps({"result": 0}))


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/users", ListUsersHandler),
        (r"/login", LoginHandler),
        (r"/is_login", VerifyLoginHandler),
    ], cookie_secret="testtest")
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
