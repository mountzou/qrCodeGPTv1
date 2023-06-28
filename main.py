import json

import quart
import quart_cors
from quart import request, Quart, request, jsonify

import qrcode
import tempfile
import os

from imgurpython import ImgurClient

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


def generate_qr_code(url, username):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name, "PNG")

    return temp_file.name


client_id = 'e42b4a7dca28816'
client_secret = '6322ed495e3cc9fc97e8d2323b9c624e16cb906f'

client = ImgurClient(client_id, client_secret)


@app.post("/qrCode/<string:username>")
async def add_QR(username):
    request_data = await request.get_json(force=True)
    url = request_data.get('url')
    temp_file_name = generate_qr_code(url, username)

    # Upload the image to Imgur and get the link
    config = {
        'album': None,
        'name': 'QR code',
        'title': 'QR code',
        'description': 'This is a QR code'
    }
    image = client.upload_from_path(temp_file_name, config=config, anon=True)
    imgur_link = image['link']

    # Remove the temporary file
    os.unlink(temp_file_name)

    return jsonify(qrCode=imgur_link), 200


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
