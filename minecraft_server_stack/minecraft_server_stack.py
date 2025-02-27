from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
    Stack, CfnOutput
)
from minecraft_server_stack.minecraft_server_instace_stack.minecraft_server_instance import MinecraftServerInstance
from minecraft_server_stack.mangenment_console.managment_console import ManagmentConsole
from constructs import Construct

class MinecraftServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        self.minecraft_server = MinecraftServerInstance(self, "MinecraftServerInstance",)
        self.management_console = ManagmentConsole(self, "ManagmentConsole", 
            instance_id=self.minecraft_server.server.instance_id,
        )
        