from flask import Flask, render_template
from monitor import ping_host
from port_scanner import check_port
from alerts import send_alert
from datetime import datetime

import threading
import json
import time

app = Flask(__name__)

with open("config.json", "r") as file:
    config = json.load(file)

hosts = config["hosts"]
ports = config["ports"]

host_status = {}

previous_host_status = {}
previous_port_status = {}


def monitor_loop():

    while True:

        for host in hosts:

            current_status, latency = ping_host(host)

            status_text = (
                "ONLINE"
                if current_status
                else "OFFLINE"
            )

            host_status[host] = {
                "status": status_text,
                "latency": latency,
                "ports": {}
            }

            if host in previous_host_status:

                if (
                    previous_host_status[host]
                    and not current_status
                ):
                    send_alert(
                        f"ALERT: {host} went OFFLINE"
                    )

                elif (
                    not previous_host_status[host]
                    and current_status
                ):
                    send_alert(
                        f"RECOVERY: {host} is ONLINE again"
                    )

            previous_host_status[host] = current_status

            if not current_status:
                continue

            for port in ports:

                port_status = check_port(
                    host,
                    port
                )

                host_status[host]["ports"][
                    str(port)
                ] = port_status

                port_key = f"{host}:{port}"

                if port_key in previous_port_status:

                    if (
                        previous_port_status[port_key]
                        and not port_status
                    ):

                        send_alert(
                            f"ALERT: {host} port {port} CLOSED"
                        )

                    elif (
                        not previous_port_status[port_key]
                        and port_status
                    ):

                        send_alert(
                            f"RECOVERY: {host} port {port} OPEN"
                        )

                previous_port_status[
                    port_key
                ] = port_status

        time.sleep(10)


@app.route("/")
def dashboard():

    total_hosts = len(host_status)

    online_hosts = sum(
        1
        for host in host_status.values()
        if host["status"] == "ONLINE"
    )

    offline_hosts = (
        total_hosts - online_hosts
    )

    if total_hosts:
        health_percentage = round(
            online_hosts
            / total_hosts
            * 100
        )
    else:
        health_percentage = 0

    try:

        with open(
            "logs/incident.logs",
            "r"
        ) as file:

            recent_alerts = (
                file.readlines()[-5:]
            )

    except FileNotFoundError:

        recent_alerts = []

    recent_alerts.reverse()

    last_updated = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return render_template(
        "dashboard.html",
        hosts=host_status,  
        ports=ports,
        total_hosts=total_hosts,
        online_hosts=online_hosts,
        offline_hosts=offline_hosts,
        health_percentage=health_percentage,
        recent_alerts=recent_alerts,
        last_updated=last_updated
    )


@app.route("/logs")
def logs_page():

    try:

        with open(
            "logs/incident.logs",
            "r"
        ) as file:

            log_lines = file.readlines()

    except FileNotFoundError:

        log_lines = []

    total_logs = len(log_lines)

    alert_count = sum(
        1
        for log in log_lines
        if "ALERT" in log
    )

    recovery_count = sum(
        1
        for log in log_lines
        if "RECOVERY" in log
    )

    log_lines.reverse()

    return render_template(
        "logs.html",
        logs=log_lines,
        total_logs=total_logs,
        alert_count=alert_count,
        recovery_count=recovery_count
    )


if __name__ == "__main__":

    monitor_thread = threading.Thread(
        target=monitor_loop,
        daemon=True
    )

    monitor_thread.start()

    app.run(
        debug=True,
        use_reloader=False
    )