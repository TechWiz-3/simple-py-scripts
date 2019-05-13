#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import hashlib
from flask import Flask, request, jsonify, render_template_string

import logging
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)


SUPPORTED_HASH_ALGOS = set(list(hashlib.algorithms_guaranteed) + ['md4'])
SUPPORTED_HASH_ALGOS = [algo for algo in SUPPORTED_HASH_ALGOS if not algo.lower().startswith('shake')]
SUPPORTED_HASH_ALGOS = sorted(SUPPORTED_HASH_ALGOS)


@app.route("/")
def index():
    return render_template_string('''\
<html>
    <head>
        <meta content='text/html; charset=UTF-8' http-equiv='Content-Type'/>
        <title>Hash</title>
        <script type="text/javascript" src="{{ url_for('static', filename='js/jquery-3.1.1.min.js') }}"></script>
        
        <style>
            #about_error {
                font-size: 120%;
                font-weight: bold;
                color: red;
            }
        </style>
            
    </head>
    <body>
        <a href="/do_hash">/do_hash</a>
        <br>
        <br>
    
        <form id="form__do_hash" method="post" action="/do_hash">
            <table><tr>
            <tr><th align="left">Text:</th><th align="left">Algorithm:</th></tr>
            <td style="vertical-align: top;">
                <textarea rows="10" cols="45" type="text" name="text" required>https://github.com/gil9red</textarea>
            </td>
            <td style="vertical-align: top;">
                <select size="10" name="hash">
                    {% for algo in algos %}
                        {% if algo|upper == "SHA1" %}
                            <option selected value="{{ algo }}">{{ algo }}</option>
                        {% else %}
                            <option value="{{ algo }}">{{ algo }}</option>
                        {% endif %}
                    {% endfor %}
                </select>
            </td>
            </tr></table>
            
            <p><input type="submit" value="Generate"></p>
        </form>
        
        <br>
        <b>Result:</b><br>
        <div id="about_error" style="display: none"></div>
        <div id="result_hash" style="display: none"></div>
        
        <script>
        $(document).ready(function() {
            $("#form__do_hash").submit(function() {
                var thisForm = this;
    
                var url = $(this).attr("action");
                var method = $(this).attr("method");
                if (method === undefined) {
                    method = "get";
                }
    
                var data = $(this).serialize();
    
                $.ajax({
                    url: url,
                    method: method,  // HTTP метод, по умолчанию GET
                    data: data,
                    dataType: "json",  // тип данных загружаемых с сервера
                    success: function(data) {
                        console.log(data);
                        console.log(JSON.stringify(data));
                        
                        var about_error = $('#about_error');
                        var result_hash = $('#result_hash');
                        
                        about_error.hide();
                        result_hash.hide();
                        
                        if (data.error != null) {
                            about_error.html(data.error);
                            about_error.show();
                        } else {
                            result_hash.html(data.result);
                            result_hash.show();
                        }
                    },
                });
    
                return false;
            });
        });
        </script>
    </body>
</html>
''', algos=SUPPORTED_HASH_ALGOS)


@app.route("/do_hash", methods=['GET', 'POST'])
def do_hash():
    print('request.args:', request.args)
    print('request.form:', request.form)
    print()

    text = request.args.get('text')
    if not text:
        text = request.form.get('text')

    algo = request.args.get('hash')
    if not algo:
        algo = request.form.get('hash')

    if not text or not algo:
        return render_template_string("""\
        Example:<br>
        <a href="{{ example_uri }}">{{ example_uri }}<a><br>
        <a href="{{ example_uri }}&hash=md5">{{ example_uri }}&hash=md5<a><br>
        <a href="{{ example_uri }}&hash=sha1">{{ example_uri }}&hash=sha1<a><br>
        <a href="{{ example_uri }}&hash=sha512">{{ example_uri }}&hash=sha512<a>
        """, example_uri='/do_hash?text=Hello World!')

    result = {
        'result': None,
        'hash': algo,
        'error': None,
    }

    if algo not in SUPPORTED_HASH_ALGOS:
        result['error'] = f'Unsupported algorithm "{algo}"'
    else:
        digest = hashlib.new(algo, data=text.encode())
        hex_digest = digest.hexdigest()

        result['result'] = hex_digest

    # Вернется json c результатом хеширования
    return jsonify(result)


if __name__ == "__main__":
    app.debug = True

    # Localhost
    app.run(
        port=5001,
        threaded=True,
    )

    # # Public IP
    # app.run(
    #     host='0.0.0.0',
    #     port=5000,
    #     threaded=True,
    # )
