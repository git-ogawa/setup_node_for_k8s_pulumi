# setup_node_for_k8s_pulumi

This project is to create Virtual machines for k8s cluster on AWS using pulumi instead of terraform in [setup_node_for_k8s](https://github.com/git-ogawa/setup_node_for_k8s).

# Requirements

The following required to use the project.

- ansible: Install with `pip install ansible`.
- python modules: Install with `pip install -r requirements.txt`
- Pulumi: See [pulumi website](https://www.pulumi.com/docs/install/) for installation.

# Prerequisite

See [setup_node_for_k8s README](https://github.com/git-ogawa/setup_node_for_k8s?tab=readme-ov-file#prerequisite).

In inventory variables, `stack_name` and `project_name` corresponding to the stack and project name in pulumi respectively. See [Organizing Pulumi projects & stacks](https://www.pulumi.com/docs/using-pulumi/organizing-projects-stacks/) for details.

Create a pulumi account and [sign in](https://app.pulumi.com/signin) is also required.

# Usage

## Create VMs

Run `create.yml` to create the resources.

```
$ ansible-playbook create.yml
```

The playbook runs `pulumi up` to the instances and the associated resources on AWS.

## Delete

Run `delete.yml`.

```
$ ansible-playbook delete.yml
```

The playback runs `pulumi destroy` to remove the all resources.

