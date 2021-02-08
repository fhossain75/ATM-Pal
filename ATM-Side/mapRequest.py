import geocoder
import requests
import urllib.parse

g = geocoder.ip('me')
centerSearch = str(g.latlng[0]) + "," + str(g.latlng[1])
center = "\"" + str(g.latlng[0]) + "," + str(g.latlng[1]) + "\""
zoom = 12
size = "400x400"
key = "AIzaSyC1YvHmJqbzSCpLIJ9dJz-CP5SKnxxeqm4"
findATM = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=ATM&inputtype=textquery&fields=formatted_address&locationbias=circle:8000@" + centerSearch + "&key=" + key
response = requests.get(findATM)
markers = "color:blue%7Clabel:S%7C " + response.json()['candidates'][0]['formatted_address']
response = requests.get("https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + str(zoom) + "&size=" + size + "&markers=" + markers + "&key=" + key)
if response.status_code == 200:
    with open("./map.jpg", 'wb') as f:
        f.write(response.content)
