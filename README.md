# Deploy
Development tool for painless pushes to dev instances. I have been realizing over the past few months that I lost a lot of time deploying code on servers. Since most of the time, projects are small, docker is not of interest. This tools aims at bringing the pain out of code transfer and service deploy/restarts. This tool will rely on ssh, git and supervisor.

## Draft

This utility will consist of 2 primary commands, "init" and "now".

#### > deploy init

init is the command that will be used to generate the configuration file. The configuration file will somewhat look like the following (tbd): 

```json
{
   "server": "",
   "user": "",
   "pwd": "",
   "project": {
      "name": "",
      "preset": "",
      "directories ": {
         "source": "",
         "build": ""
      }
   },
   "scripts": {
      "before": [],
      "test": [],
      "build": [],
      "after": []
   }
}
```

#### > deploy now

now pushes the lastest changes to the server and restarts the service. 
