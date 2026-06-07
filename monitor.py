import subprocess
import platform
import re


def ping_host(host):

    param = "-n" if platform.system().lower() == "windows" else "-c"

    command = ["ping", param, "1", host]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        online = result.returncode == 0

        latency = None

        if online:

            output = result.stdout

            match = re.search(r"time[=<](\d+)", output)

            if match:
                latency = int(match.group(1))

        return online, latency

    except Exception:
        return False, None