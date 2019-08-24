# Python OAuth2.0
这是一个基于tornado框架的OAuth2.0协议的完整实现。对于OAuth2.0的描述请关注`附录、参考文献`

* 角色和职责:
    * 用户登陆鉴权服务
        * login页面，提供用户输入账号密码的页面
        * login接口, 用户的账号密码换取用户登陆态票据
        * verify接口, 用于对用户登陆态进行鉴权
    * OAuth2.0授权服务
        * authorize接口, 校验用户登陆态重定向到第三方
        * token接口，第三方用授权码换取access_token
        * 资源服务, 第三方使用access_token换取用户资源
        * PKCE, 用于保护授权码。
    * 第三方应用
        * 提供用户登陆入口
        * 获取access_token
        * 使用access_token到OAuth请求用户资源服务

编写该服务的目的其实主要是熟悉tornado `^_^`


## 附录、参考文献
* [The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
