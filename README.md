
# Welcome to my AWS Spot hosted Minecraft Server CDK Project

This is a CDK project to setup hosting a minecraft server on spot intances that will automatically turn off when nobondy is online to save costs. It also generates a website for managing the minecraft server. Primarily for personal use.

In order to use this for yourself, first create a new venv enviroment.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now deploy the app to your AWS account

```
$ cdk deploy
```

When this is finished running, it will output the domain name of the managment console where you turn on the server and find its IP address.
Note that since there is no elastic IP assigned to the instance, the IP will change each time the server is turned on and off

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
