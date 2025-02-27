#!/usr/bin/env python3
import os

import aws_cdk as cdk

from minecraft_server_stack.minecraft_server_stack import MinecraftServerStack


app = cdk.App()
MinecraftServerStack(app, "MinecraftServerStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
