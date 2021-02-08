#This will help us generate QR codes for our raspberry pi atm
import pyqrcode
import json
dictionary = {"u": "HACKATHONUSER220","p":"uga123","amt":"500"}
json_object = json.dumps(dictionary, indent = 4)   

import qrcode
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=20,
    border=4,
)
qr.add_data(json_object)
#qr.add_data("Hello World")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("text3.png")
