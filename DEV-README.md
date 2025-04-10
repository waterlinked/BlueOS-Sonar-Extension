### For Developers

This BlueOS extention is based on the 
[BlueOS-Water-Linked-DVL extention](https://github.com/bluerobotics/BlueOS-Water-Linked-DVL?tab=readme-ov-file)

## Compiling Docker Image

Used this once:
```bash
docker buildx create --use
```

Login with `docker login`, with username `-u [username]`

Build for the onboard RPi and push to dockerhub:
```bash
docker buildx build --platform linux/arm/v7 -t waterlinked/blueos-sonar-extension:latest --push .
```

For the settings in BLueOS I used same as DVL in Original settings:

```json
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
```