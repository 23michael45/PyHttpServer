
import requests

#http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file

#url = "http://111.230.250.213:8000/"
url = "http://localhost:8000/"
fin = open('Distribution/V1/v1test.dll', 'rb')
dic = {'file': fin ,'data':'Distribution/V1/'}



multipart_form_data = {
    'file': ('Distribution/V1/v1.dll', open('Distribution/V1/v1test.dll', 'rb')),
    'action': ('', 'store'),
    'path': ('', 'Distribution/V1/')
}

try:
  r = requests.post(url, files=multipart_form_data)
  print(r.text)
finally:
	fin.close()