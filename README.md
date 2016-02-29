# Deploy
Development tool for painless pushes to dev instances. I have been realizing over the past few months that I lost a lot of time deploying code on servers. Since most of the time, projects are small, docker is not of interest. This tools aims at bringing the pain out of code transfer and service deploy/restarts. This tool will rely on ssh, git and supervisor.

## Draft

This utility will consist of 2 primary commands, "init" and "now".

#### > deploy init

init is the command that will be used to generate the configuration file. The configuration file will somewhat look like the following (tbd): 

```
{
    "project": {
        "directories": {
            "build": "",
            "source": ""
        },
        "name": "",
        "preset": ""
    },
    "scripts": {
        "after": [],
        "before": [],
        "test": []
    },
    "server": {
        "address": "",
        "user": ""
    }
}
```

#### > deploy now

now pushes the latest changes to the server and restarts the service.


## Things to be figured out

- How to abstract the presets so that it can apply to multiple languages, both compiled and interpreted.
- Languages version requirement
- Package managers
- Manage artifacts, binaries
