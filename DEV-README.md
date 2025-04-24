### For Developers

This BlueOS extension is based on the 
[BlueOS-Water-Linked-DVL extension](https://github.com/bluerobotics/BlueOS-Water-Linked-DVL?tab=readme-ov-file)

## Compiling Docker Image

Used this once:
```bash
docker buildx create --use
```

Login with `docker login`, with username `-u [username]`

Build for the onboard RPi and push to dockerhub:\
(This command gives the Docker image the version tag *latest*, for release please adhere to the versioning in the [README](./README.md))
```bash
docker buildx build --platform linux/arm/v7 -t waterlinked/blueos-sonar-extension:latest --push .
```

For the settings in BLueOS I used same as DVL in Original settings:

```json
{
  "ExposedPorts": {
    "80/tcp": {}
  },
  "HostConfig": {
    "Binds": [
      "/root/.config:/root/.config"
    ],
    "ExtraHosts": [
      "host.docker.internal:host-gateway"
    ],
    "PortBindings": {
      "80/tcp": [
        {
          "HostPort": ""
        }
      ]
    }
  }
}
```