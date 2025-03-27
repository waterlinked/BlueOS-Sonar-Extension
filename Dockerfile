FROM python:3.9-slim-bullseye

RUN apt update && apt install -y nmap

# Create default user folder
RUN mkdir -p /home/pi

# Install dvl service
COPY app /home/pi/app
RUN cd /home/pi/app && pip3 install .

LABEL version="1.0.0"
LABEL permissions='\
{\
 "ExposedPorts": {\
   "9001/tcp": {}\
  },\
  "HostConfig": {\
    "Binds":["/root/.config:/root/.config"],\
    "ExtraHosts": [\
      "host.docker.internal:host-gateway"\
    ],\
    "PortBindings": {\
      "9001/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    }\
  }\
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
        "3dsonar",\
        "point-cloud",\
        "waterlinked"\
    ]'
LABEL readme='https://raw.githubusercontent.com/waterlinked/BlueOS-Sonar-Extention/{tag}/README.md'
LABEL links='{\
        "website": "https://github.com/waterlinked/BlueOS-Sonar-Extention",\
        "support": "https://github.com/waterlinked/BlueOS-Sonar-Extention/issues"\
    }'
LABEL requirements="core >= 1.1"

ENTRYPOINT /home/pi/app/main.py