from flask import request, jsonify
from urllib.parse import unquote_plus

"""
General API resource utils.
"""


def log_error(msg, err):
    return msg.format(err)


def handle_exception(err, msg, err_code):
    log_error(msg + ' Error:{0}', err)
    return jsonify(message=msg), err_code


def get_query_param_str(param):
    param_value = request.args.get(param)
    return unquote_plus(param_value).strip() if param_value and isinstance(param_value, str) else None