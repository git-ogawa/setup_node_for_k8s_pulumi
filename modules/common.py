def get_os_user(os: str) -> str:
    if "ubuntu" in os:
        return "ubuntu"
    elif "rocky" in os:
        return "rocky"
