from logger import log_event


def send_alert(message):

    print(message)

    log_event(message)