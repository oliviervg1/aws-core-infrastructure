from troposphere import Ref, Output
from troposphere.ec2 import RouteTable, Route
from troposphere.ec2 import Subnet, SubnetRouteTableAssociation
from troposphere.ec2 import Tag

from stacker.blueprints.base import Blueprint


class Subnets(Blueprint):

    VARIABLES = {
        "VpcId": {
            "type": str,
            "description": "Vpc ID"
        },
        "IgwId": {
            "type": str,
            "description": "Internet Gateway ID"
        },
        "Subnets": {
            "type": list,
            "description": "List of subnets"
        }
    }

    def to_camel_case(self, string_to_convert):
        return "".join([i.capitalize() for i in string_to_convert.split("-")])

    def add_route_table(
        self, Tier=None, Type=None, AZ=None, Cidr=None, Tags=None
    ):
        variables = self.get_variables()
        if Type == "public":
            rt_logical_id = "{0}RouteTable".format(Tier.capitalize())
            route_table_name = "{0}-rtb".format(Tier)
        else:
            rt_logical_id = "{0}RouteTable{1}".format(
                Tier.capitalize(), self.to_camel_case(AZ)
            )
            route_table_name = "{0}-rtb-{1}".format(Tier, AZ)

        route_table = RouteTable(
            rt_logical_id,
            VpcId=variables["VpcId"],
            Tags=[Tag("Name", "{0}-{1}".format(
                self.context.namespace, route_table_name
            ))]
        )
        self.resources[rt_logical_id] = route_table

        if Type == "public":
            route_logical_id = "{0}InternetAccess".format(Tier.capitalize())
            self.resources[route_logical_id] = Route(
                route_logical_id,
                GatewayId=variables["IgwId"],
                DestinationCidrBlock="0.0.0.0/0",
                RouteTableId=Ref(route_table)
            )

        rt_output_logical_id = "{0}Id".format(rt_logical_id)
        self.outputs[rt_output_logical_id] = Output(
            rt_output_logical_id,
            Description="Route Table ID",
            Value=Ref(route_table)
        )

        return rt_logical_id

    def add_subnet(
        self, rt_logical_id, Tier=None, Type=None, AZ=None, Cidr=None,
        Tags=None
    ):
        variables = self.get_variables()

        subnet_logical_id = "{0}Subnet{1}".format(
            Tier.capitalize(), self.to_camel_case(AZ)
        )
        subnet = Subnet(
            subnet_logical_id,
            CidrBlock=Cidr,
            AvailabilityZone=AZ,
            VpcId=variables["VpcId"],
            MapPublicIpOnLaunch=True if Type == "public" else False,
            Tags=[Tag(key, value) for key, value in Tags.iteritems()]
        )
        self.resources[subnet_logical_id] = subnet

        subnet_output_logical_id = "{0}Id".format(subnet_logical_id)
        self.outputs[subnet_logical_id] = Output(
            subnet_output_logical_id,
            Description="Subnet ID",
            Value=Ref(subnet)
        )

        subnet_rt_assoc_logical_id = "{0}RtbAssociation{1}".format(
            Tier.capitalize(), self.to_camel_case(AZ)
        )
        subnet_rt_assoc = SubnetRouteTableAssociation(
            subnet_rt_assoc_logical_id,
            SubnetId=Ref(subnet),
            RouteTableId=Ref(self.resources[rt_logical_id])
        )
        self.resources[subnet_rt_assoc_logical_id] = subnet_rt_assoc

    def create_template(self):
        variables = self.get_variables()
        self.resources = {}
        self.outputs = {}
        for subnet in variables["Subnets"]:
            rt_logical_id = self.add_route_table(**subnet)
            self.add_subnet(rt_logical_id, **subnet)
        self.template.add_resource(self.resources.values())
        self.template.add_output(self.outputs.values())
