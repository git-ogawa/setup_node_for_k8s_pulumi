from pulumi_aws import ec2, vpc


def subnet(project: str, vpc_id: str, cidr_block: str) -> ec2.Subnet:
    subnet_name = f"{project}-subnet"
    _subnet = ec2.Subnet(
        subnet_name,
        vpc_id=vpc_id,
        cidr_block=cidr_block,
        tags={"Name": subnet_name, "Project": project},
    )
    return _subnet


def security_group(project: str, vpc_id: str) -> ec2.SecurityGroup:
    security_group_name = f"{project}-sg"
    _sg = ec2.SecurityGroup(
        security_group_name,
        description="Allow TLS inbound traffic and all outbound traffic",
        vpc_id=vpc_id,
        tags={
            "Name": security_group_name,
            "Project": project,
        },
    )
    add_sg_rule(_sg.id)
    return _sg


def add_sg_rule(security_group_id: str) -> None:
    vpc.SecurityGroupIngressRule(
        "http",
        description="http",
        ip_protocol="tcp",
        from_port=80,
        to_port=80,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "http"},
    ),
    vpc.SecurityGroupIngressRule(
        "https",
        description="https",
        ip_protocol="tcp",
        from_port=443,
        to_port=443,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "https"},
    ),
    vpc.SecurityGroupIngressRule(
        "ssh",
        description="ssh",
        ip_protocol="tcp",
        from_port=22,
        to_port=22,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "ssh"},
    )
    vpc.SecurityGroupIngressRule(
        "api server",
        description="api server",
        ip_protocol="tcp",
        from_port=6443,
        to_port=6443,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "api server"},
    )
    vpc.SecurityGroupIngressRule(
        "etcd client",
        description="etcd client",
        ip_protocol="tcp",
        from_port=2379,
        to_port=2380,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "etcd client"},
    )
    vpc.SecurityGroupIngressRule(
        "kubelet api",
        description="kubelet api",
        ip_protocol="tcp",
        from_port=10250,
        to_port=10250,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "kubelet api"},
    )
    vpc.SecurityGroupIngressRule(
        "kube controller manager",
        description="kube controller manager",
        ip_protocol="tcp",
        from_port=10257,
        to_port=10257,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "kube controller manager"},
    )
    vpc.SecurityGroupIngressRule(
        "node port",
        description="node port",
        ip_protocol="tcp",
        from_port=30000,
        to_port=32767,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
        tags={"Name": "node port"},
    )
    vpc.SecurityGroupEgressRule(
        "all allow",
        ip_protocol=-1,
        security_group_id=security_group_id,
        cidr_ipv4="0.0.0.0/0",
    )
