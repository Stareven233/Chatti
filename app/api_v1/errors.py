from . import v1
from flask import jsonify

response = {'code': 0, 'msg': ""}


@v1.app_errorhandler(401)
def authorize_failed(e):
    # Flask_RESTful Api 传的参数，exception类型
    response['code'] = 1001
    response['msg'] = "认证失败"
    return jsonify(response), 401


@v1.app_errorhandler(403)
def forbidden(e):
    response['code'] = 1002
    response['msg'] = "禁止访问"
    return jsonify(response), 403


@v1.app_errorhandler(404)
def not_found(e):
    response['code'] = 2001
    response['msg'] = "资源不存在"
    return jsonify(response), 404


@v1.app_errorhandler(400)
def bad_request(e):
    response['code'] = 2002
    response['msg'] = "缺少或包含了多余的请求参数"
    return jsonify(response), 400


@v1.app_errorhandler(500)
def server_error(e):
    response['code'] = 3001
    response['msg'] = "服务器错误"
    return jsonify(response), 500
