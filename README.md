# BlueOS Extention for Water Linked Sonar 3D-15 
BlueOS Extention for finding the sonar IP and displaying the website within BlueOS


mostly copied from https://github.com/bluerobotics/BlueOS-Water-Linked-DVL
also copied a little from https://github.com/waterlinked/blueos-ugps-extension

slimed down the index.html to get rid of things not needed


### Dev

used this once:
```bash
docker buildx create --use
```

login with `docker login`, with username `-u [username]`

build and push to dockerhub:
```bash
docker buildx build --platform linux/arm/v7 -t waterlinked/blueos-sonar-extension:latest --push .
```

used same as DVL in Original settings:
{
  "ExposedPorts": {
    "9001/tcp": {}
  },
  "HostConfig": {
    "Binds": [
      "/root/.config:/root/.config"
    ],
    "ExtraHosts": [
      "host.docker.internal:host-gateway"
    ],
    "PortBindings": {
      "9001/tcp": [
        {
          "HostPort": ""
        }
      ]
    }
  }
}

works on wifi but not LAN (could not find it with: `nmap -sn 192.168.2.0/24
` either)