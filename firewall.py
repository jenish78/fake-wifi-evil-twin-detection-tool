import subprocess

def disconnect_wifi():
    try:
        # Get interface name automatically
        result = subprocess.check_output(
            "netsh wlan show interfaces",
            shell=True
        ).decode()

        interface = None
        for line in result.split("\n"):
            if "Name" in line:
                interface = line.split(":",1)[1].strip()
                break

        if interface:
            cmd = f'netsh wlan disconnect interface="{interface}"'
            subprocess.run(cmd, shell=True)
            return f"Disconnected from {interface}"
        else:
            return "No interface found"

    except Exception as e:
        return str(e)


def block_network(ssid):
    try:
        cmd = f'netsh wlan add filter permission=block ssid="{ssid}" networktype=infrastructure'
        subprocess.run(cmd, shell=True)
        return f"{ssid} blocked"
    except Exception as e:
        return str(e)