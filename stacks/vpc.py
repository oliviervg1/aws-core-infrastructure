from troposphere import Output, Ref
from troposphere.ec2 import VPC as TroposphereVPC
from troposphere.ec2 import InternetGateway, VPCGatewayAttachment
from troposphere.ec2 import Tag

from stacker.blueprints.base import Blueprint


class VPC(Blueprint):

    VARIABLES = {
        "VpcCidr": {
            "type": str
        },
        "Tags": {
            "type": list
        }
    }

    def create_vpc(self):
        variables = self.get_variables()
        self.vpc = self.template.add_resource(TroposphereVPC(
            "VPC",
            CidrBlock=variables["VpcCidr"],
            InstanceTenancy="default",
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=[
                Tag(key, value)
                for key, value in variables["Tags"].iteritems()
            ]
        ))

        self.template.add_output(Output(
            "VpcId",
            Description="VPC ID",
            Value=Ref(self.vpc)
        ))

    def create_internet_gateway(self):
        variables = self.get_variables()
        self.igw = self.template.add_resource(InternetGateway(
            "InternetGateway",
            DependsOn="VPC",
            Tags=[
                Tag(key, value)
                for key, value in variables["Tags"].iteritems()
            ]
        ))

        self.template.add_resource(VPCGatewayAttachment(
            "IGWAttachment",
            DependsOn="InternetGateway",
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(self.igw)
        ))

        self.template.add_output(Output(
            "IgwId",
            Description="Internet Gateway ID",
            Value=Ref(self.igw)
        ))

    def create_template(self):
        self.create_vpc()
        self.create_internet_gateway()
