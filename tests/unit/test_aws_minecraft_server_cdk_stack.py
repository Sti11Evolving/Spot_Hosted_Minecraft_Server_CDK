import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_minecraft_server_cdk.aws_minecraft_server_cdk_stack import AwsMinecraftServerCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_minecraft_server_cdk/aws_minecraft_server_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsMinecraftServerCdkStack(app, "aws-minecraft-server-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
