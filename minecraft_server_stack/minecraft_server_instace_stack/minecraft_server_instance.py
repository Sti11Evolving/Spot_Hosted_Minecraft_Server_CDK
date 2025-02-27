from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnParameter
)
from constructs import Construct
import random
import string

MINECRAFT_PATH = "/usr/MinecraftServer"
MINECRAFT_ASSET_PATH = "./assets/MinecraftServer"
MINECRAFT_MANAGER_PATH = "/usr/MinecraftServerManager"
MINECRAFT_MANAGER_ASSET_PATH = "./assets/MinecraftServerManager"
WORLD_PATH = "/usr/world"

class MinecraftServerInstance(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Creates a random 20 character string for the rcon password
        # This doesn't need to be very secure since the RCON port is blocked from the internet
        RCON_PASSWORD = ''.join( [random.choice(string.ascii_letters + string.digits) for i in range(0,20)] )

        TIMEOUT_MINUTES = CfnParameter(self, "TimeoutMinutes", 
            type="Number", 
            default=30,
            description="The number of minutes to wait for players to join before shutting down the server",
            min_value=5
        )

        # Creates the VPC that will host the Minecraft Server
        # Creates the VPC that will host the Minecraft Server
        # Only needs Public Subnets since the server will be hosted on the internet
        # We want to have subnets in every availability zone to increase the avaliable placements for our spot instances
        self.vpc = ec2.Vpc(self, "MinecraftVPC",
            ip_addresses=ec2.IpAddresses.cidr("11.11.11.0/28"),
            create_internet_gateway=True,
            availability_zones=["us-east-2c"],
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="ServerSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            },
        )

        # The security group for the Minecraft Server
        self.server_sg = ec2.SecurityGroup(self, "MinecraftServerInstanceSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )
        self.server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(25565))
        self.server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        self.server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))

        restart_handle = ec2.InitServiceRestartHandle()

        # The instance that will host the Minecraft Server
        self.server = ec2.Instance(self, "MinecraftServerInstance",
            vpc=self.vpc,
            instance_type=ec2.InstanceType("c7a.xlarge"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=self.server_sg,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=30,
                    )
                )
            ],
            init=ec2.CloudFormationInit.from_config_sets(
                config_sets={
                    "default": [ "install_source", "install_packages", "configure_services" ]
                },
                configs={
                    "install_source": ec2.InitConfig([
                        ec2.InitSource.from_asset(
                            target_directory=MINECRAFT_PATH,
                            path=MINECRAFT_ASSET_PATH,
                            service_restart_handles=[restart_handle],
                        ),
                        ec2.InitSource.from_asset(
                            target_directory=MINECRAFT_MANAGER_PATH,
                            path=MINECRAFT_MANAGER_ASSET_PATH,
                            service_restart_handles=[restart_handle],
                        ),
                        ec2.InitFile.from_string(
                            file_name=f"{MINECRAFT_MANAGER_PATH}/.env",
                            content=f"RCON_PASSWORD={RCON_PASSWORD}\nMINECRAFT_PATH={MINECRAFT_PATH}\nTIMEOUT_MINUTES={TIMEOUT_MINUTES.value_as_number}\n",
                        ),
                    ]),
                    "install_packages": ec2.InitConfig([
                        ec2.InitPackage.yum("java-21-amazon-corretto-headless",
                            service_restart_handles=[restart_handle]
                        ),
                        ec2.InitCommand.shell_command("sudo yum install -y python-pip"),
                        ec2.InitCommand.shell_command("sudo pip install -r requirements.txt",
                            cwd=MINECRAFT_MANAGER_PATH
                        ),
                        #ec2.InitCommand.shell_command('openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=Sti11Evolving/OU=Sti11Evolving/CN=MinecraftServerManager"')
                    ]),
                    "configure_services": ec2.InitConfig([
                        ec2.InitService.systemd_config_file("MinecraftManager",
                            command="/usr/local/bin/gunicorn --bind 0.0.0.0:80 app:app",
                            cwd=MINECRAFT_MANAGER_PATH
                        ),
                        ec2.InitService.enable("MinecraftManager",
                            service_restart_handle=restart_handle
                        ),
                    ])
                }
            ),
        )

        # Turns the instance into a spot instance
        self.test_launch_template = ec2.LaunchTemplate(self, "SpotLaunchTemplate",
            spot_options=ec2.LaunchTemplateSpotOptions(
                interruption_behavior=ec2.SpotInstanceInterruption.STOP,
                request_type=ec2.SpotRequestType.PERSISTENT,
            ),
        )
        self.server.instance.launch_template = ec2.CfnInstance.LaunchTemplateSpecificationProperty(
            version=self.test_launch_template.latest_version_number,
            launch_template_id=self.test_launch_template.launch_template_id
        )

        # Enable connecting via session manager
        self.server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )