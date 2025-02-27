from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    CfnOutput, RemovalPolicy, Duration
)
from constructs import Construct
from deploy_time_build import NodejsBuild

class ManagmentConsole(Construct):

    def __init__(self, scope: Construct, construct_id: str, instance_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        instance_info_lambda = lambda_.Function(self, "InstanceInfoLambda",
            handler="instance_info.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset(
                "./assets/lambda/instance_info",
                deploy_time=True
            ),
            environment={
                "INSTANCE_ID": instance_id
            },
            timeout=Duration.seconds(20)
        )

        # Allow the lambda to describe the minecraft server instance
        instance_info_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess")
        )

        start_instance_lambda = lambda_.Function(self, "StartInstanceLambda",
            handler="start_instance.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset(
                "./assets/lambda/start_instance",
                deploy_time=True
            ),
            environment={
                "INSTANCE_ID": instance_id
            },
            timeout=Duration.seconds(10)
        )

        start_instance_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess")
        )

        stop_instance_lambda = lambda_.Function(self, "StopInstanceLambda",
            handler="stop_instance.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset(
                "./assets/lambda/stop_instance",
                deploy_time=True
            ),
            environment={
                "INSTANCE_ID": instance_id
            },
            timeout=Duration.seconds(10)
        )

        stop_instance_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess")
        )

        minecraft_server_manager_api = apigateway.RestApi(self, "MinecraftServerManagerAPI",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS
            )
        )

        server_info_resource = minecraft_server_manager_api.root.add_resource("instance_info")
        server_info_resource.add_method("GET",
            apigateway.LambdaIntegration(instance_info_lambda)
        )

        start_instance_resource = minecraft_server_manager_api.root.add_resource("start_instance")
        start_instance_resource.add_method("POST",
            apigateway.LambdaIntegration(start_instance_lambda)
        )

        stop_instance_resource = minecraft_server_manager_api.root.add_resource("stop_instance")
        stop_instance_resource.add_method("POST",
            apigateway.LambdaIntegration(stop_instance_lambda)
        )

        website_bucket = s3.Bucket(self, "WebsiteBucket",
            website_index_document="index.html",
            access_control = s3.BucketAccessControl.PRIVATE,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        distribution = cloudfront.Distribution(self, "Distribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(website_bucket),
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            )
        )

        CfnOutput(self, "DistributionDomainName", 
            value=distribution.domain_name,
            description="The domain name of the website"
        )

        NodejsBuild(self, "NodejsBuild",
            assets=[{
                "path": "./assets/minecraft_manager_console",
                "exclude": ["node_modules", "out"]
            }],
            destination_bucket=website_bucket,
            distribution=distribution,
            output_source_directory="out",
            build_commands=["npm ci", "npm run build"],
            output_env_file=True,
            build_environment={
                "NEXT_PUBLIC_API_URL": minecraft_server_manager_api.url
            },
        )
