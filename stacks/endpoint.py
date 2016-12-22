from troposphere import Join, Ref
from troposphere.ec2 import VPCEndpoint
from awacs.aws import Policy, Statement, Principal, Action

from stacker.blueprints.base import Blueprint


class Endpoint(Blueprint):

    VARIABLES = {
        "VpcId": {
            "type": str,
            "description": "Vpc ID"
        },
        "Service": {
            "type": str,
            "description": "Name of the service to create vpc endpoint for"
        },
        "RouteTableIds": {
            "type": list,
            "description": "List of route table ids to add endpoint to"
        }
    }

    def create_endpoint(self):
        variables = self.get_variables()
        self.template.add_resource(VPCEndpoint(
            "{0}VpcEndpoint".format(variables["Service"].capitalize()),
            ServiceName=Join("", [
                "com.amazonaws.",
                Ref("AWS::Region"),
                ".{0}".format(variables["Service"])
            ]),
            VpcId=variables["VpcId"],
            RouteTableIds=variables["RouteTableIds"],
            PolicyDocument=Policy(
                Statement=[
                    Statement(
                        Effect="Allow",
                        Action=[Action(variables["Service"], "*")],
                        Resource=["*"],
                        Principal=Principal("*")
                    )
                ]
            )
        ))

    def create_template(self):
        self.create_endpoint()
