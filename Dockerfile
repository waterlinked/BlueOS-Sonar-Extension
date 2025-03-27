# Mash of the Dockerfile from the BlueRobotics example and the Dockerfile from the Waterlinked example 
# (permissions from the Waterlinked example)

FROM python:3.10-slim-bullseye

RUN apt update && apt install -y nmap

# Create default user folder
RUN mkdir -p /home/pi

# Install sonar service
COPY app /home/pi/app
RUN cd /home/pi/app && pip3 install .

LABEL version="1.0.0"

LABEL permissions='\
{\
  "NetworkMode": "host",\
  "Env": [\
    "SONAR_HOST=http://192.168.2.95",\
    "EXTRA_ARGS="\
  ]\
}'
LABEL authors='[\
    {\
        "name": "Water Linked",\
        "email": "support@waterlinked.com"\
    }\
]'
LABEL company='{\
        "about": "",\
        "name": "Water Linked",\
        "email": "support@waterlinked.com"\
    }'
LABEL type="device-integration"
LABEL tags='[\
    "waterlinked",\
    "3dsonar"\
]'
LABEL readme='https://raw.githubusercontent.com/waterlinked/BlueOS-Sonar-Extention/{tag}/readme.md'
LABEL links='{\
    "website": "https://github.com/waterlinked/BlueOS-Sonar-Extention",\
    "support": "https://github.com/waterlinked/BlueOS-Sonar-Extention/issues"\
}'
LABEL requirements="core >= 1.1"

ENTRYPOINT /home/pi/app/main.py