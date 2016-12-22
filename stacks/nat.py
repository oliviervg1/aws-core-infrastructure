from troposphere import GetAtt, Ref
from troposphere.ec2 import NatGateway, EIP, Route

from stacker.blueprints.base import Blueprint


class NatGW(Blueprint):

    VARIABLES = {
        "PublicSubnetIds": {
            "type": list,
            "description": "List of public subnet IDs to deploy NAT Gateway in"
        },
        "PrivateRouteTableIds": {
            "type": list,
            "description": (
                "List of private route table IDs where the NAT gateway "
                "should be added as a route for internet access"
            )
        },
        "HighAvailability": {
            "type": bool,
            "description": (
                "Set to true to deploy a NAT Gateway per Availability Zones"
            )
        }
    }

    def create_eips(self):
        variables = self.get_variables()

        if variables["HighAvailability"]:
            for i in range(len(variables["PublicSubnetIds"])):
                self.nat_eips.append(self.template.add_resource(EIP(
                    "NatEip{}".format(i),
                    Domain="vpc"
                )))
        else:
            self.nat_eips.append(self.template.add_resource(EIP(
                "NatEip",
                Domain="vpc"
            )))

    def create_nat_gateways(self):
        variables = self.get_variables()

        nats = []
        if variables["HighAvailability"]:
            for i, subnet_id in enumerate(variables["PublicSubnetIds"]):
                nats.append(self.template.add_resource(NatGateway(
                    "Nat{}".format(i),
                    AllocationId=GetAtt(self.nat_eips[i], "AllocationId"),
                    SubnetId=subnet_id
                )))
        else:
            nats.append(self.template.add_resource(NatGateway(
                "Nat",
                AllocationId=GetAtt(self.nat_eips[0], "AllocationId"),
                SubnetId=variables["PublicSubnetIds"][0]
            )))

        for i, route_table_id in enumerate(variables["PrivateRouteTableIds"]):
            self.template.add_resource(Route(
                "NatRoute{0}".format(i),
                RouteTableId=route_table_id,
                DestinationCidrBlock="0.0.0.0/0",
                NatGatewayId=(
                    Ref(nats[i % len(variables["PublicSubnetIds"])])
                    if variables["HighAvailability"] else Ref(nats[0])
                )
            ))

    def create_template(self):
        self.nat_eips = []
        self.create_eips()
        self.create_nat_gateways()
