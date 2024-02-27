import argparse
from dataclasses import dataclass
from pathlib import Path

import pulumi
from jinja2 import Environment, FileSystemLoader
from pulumi import automation as auto
from pulumi_aws import ec2
from ruamel.yaml import YAML

from modules.instance import Node
from modules.network import security_group, subnet


def run():
    yaml = YAML()
    with open("inventory.yml") as f:
        inventory = yaml.load(f)

    vars = inventory["all"]["vars"]
    project_name = vars["project_name"]

    default_vpc = ec2.get_vpc(default=True)
    public_subnet = subnet(
        project_name, vpc_id=default_vpc.id, cidr_block=vars["subnet_cidr"]
    )
    security_group(project_name, vpc_id=default_vpc.id)

    memory = vars["memory"]
    vcpu = vars["vcpu"]
    key_name = vars["key_name"]

    control_plane = [i for i in vars["control_plane"]]
    workers = [i for i in vars["workers"]]

    for nodes in [control_plane, workers]:
        for node in nodes:
            _instance = Node(
                node["hostname"],
                os=node["os"],
                subnet=public_subnet.id,
                vcpu=vcpu,
                memory=memory,
                key_name=key_name,
            )
            _instance.setup()
            pulumi.export(f"{node['hostname']}-public_ip", _instance.instance.public_ip)
            pulumi.export(
                f"{node['hostname']}-private_ip", _instance.instance.private_ip
            )


@dataclass
class Stack:
    stack_name: str
    project_name: str
    region: str

    def setup(self):
        self.stack = auto.create_or_select_stack(
            stack_name=self.stack_name, project_name=self.project_name, program=run
        )
        self.stack.workspace.install_plugin("aws", "v4.0.0")
        self.stack.refresh(on_output=print)
        self.stack.set_config("aws:region", auto.ConfigValue(value=self.region))

    def load_inventory(self):
        yaml = YAML()
        with open("inventory.yml") as f:
            self.inventory = yaml.load(f)

    def up(self):
        up_result = self.stack.up(on_output=print)
        return up_result

    def destroy(self):
        self.stack.destroy(on_output=print)

    def generate_inventory(self, up_result):
        yaml = YAML()
        with open("inventory.yml") as f:
            inventory = yaml.load(f)

        vars = inventory["all"]["vars"]
        key_name = vars["key_name"]
        variables = {"key_name": key_name, "_control_plane": [], "_workers": []}

        control_plane_hosts = vars["control_plane"]
        for node in control_plane_hosts:
            node["public_ip"] = up_result.outputs[f"{node['hostname']}-public_ip"].value
            node["private_ip"] = up_result.outputs[
                f"{node['hostname']}-private_ip"
            ].value
            variables["_control_plane"].append(node)

        worker_hosts = vars["workers"]
        for node in worker_hosts:
            node["public_ip"] = up_result.outputs[f"{node['hostname']}-public_ip"].value
            node["private_ip"] = up_result.outputs[
                f"{node['hostname']}-private_ip"
            ].value
            variables["_workers"].append(node)

        p = Path("templates")
        env = Environment(
            loader=FileSystemLoader(p, encoding="utf8"),
            lstrip_blocks=True,
            trim_blocks=True,
            keep_trailing_newline=True,
        )
        tmpl = env.get_template("template_inventory.yml.j2")
        with open("template_inventory.yml", "w") as f:
            f.write(tmpl.render(variables))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--action",
        type=str,
        choices=["up", "destroy"],
        help="Action to pulumi",
        required=True,
    )
    parser.add_argument(
        "-s", "--stack", type=str, help="Pulumi stack name", required=True
    )
    parser.add_argument(
        "-p", "--project", type=str, help="Pulumi project name", required=True
    )
    parser.add_argument(
        "-r", "--region", type=str, help="AWS region name", required=True
    )
    args = parser.parse_args()

    stack = Stack(stack_name=args.stack, project_name=args.project, region=args.region)
    stack.setup()

    if args.action == "up":
        result = stack.up()
        stack.generate_inventory(result)
    elif args.action == "destroy":
        stack.destroy()
