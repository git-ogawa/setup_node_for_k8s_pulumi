from dataclasses import dataclass

from pulumi_aws import ec2


@dataclass
class Node:
    name: str
    os: str
    subnet: str
    key_name: str
    vcpu: int
    memory: int
    volume_size: int = 20

    def setup(self) -> None:
        ami = self.get_ami()
        instance_type = self.get_instance_types()
        instance_type_id = self.get_instance_type(instance_type)
        self.instance = self.ec2_instance(ami=ami.id, instance_type=instance_type_id)

    def get_ami(self) -> ec2.GetAmiResult:
        owners = {"canonical": "099720109477", "rockylinux": "792107900819"}

        os_name, version, arch = self.os.split("-")

        if os_name == "ubuntu":
            search = f"ubuntu/images/hvm-ssd/ubuntu-*-{version}-{arch}*"
            owner = owners["canonical"]
        elif os_name == "rockylinux":
            if arch == "amd64":
                search = f"Rocky-9-EC2-Base-{version}-*.x86_64*"
            elif arch == "arm64":
                search = f"Rocky-9-EC2-Base-{version}-*.aarch64*"
            owner = owners["rockylinux"]

        _ami = ec2.get_ami(
            most_recent=True,
            filters=[
                ec2.GetAmiFilterArgs(
                    name="name",
                    values=[search],
                ),
            ],
            owners=[owner],
        )
        return _ami

    def ec2_instance(self, ami: str, instance_type: str) -> ec2.Instance:
        user_data = f"""#!/bin/bash
        hostnamectl set-hostname {self.name}
        """
        _instance = ec2.Instance(
            self.name,
            ami=ami,
            instance_type=instance_type,
            tags={
                "Name": self.name,
            },
            subnet_id=self.subnet,
            key_name=self.key_name,
            associate_public_ip_address=True,
            user_data=user_data,
            root_block_device=ec2.InstanceRootBlockDeviceArgs(
                volume_size=self.volume_size
            ),
        )
        return _instance

    def get_instance_type(self, instance_type: str) -> str:
        return ec2.get_instance_type(instance_type=instance_type).id

    def get_instance_types(self) -> str:
        families = ["m6*", "t2*"]
        memory_mib = self.memory * 1024

        types = ec2.get_instance_types(
            filters=[
                ec2.GetInstanceTypesFilterArgs(name="instance-type", values=families),
                ec2.GetInstanceTypesFilterArgs(
                    name="memory-info.size-in-mib",
                    values=[memory_mib],
                ),
                ec2.GetInstanceTypesFilterArgs(
                    name="vcpu-info.default-vcpus",
                    values=[self.vcpu],
                ),
            ]
        )
        return types.instance_types[0]
