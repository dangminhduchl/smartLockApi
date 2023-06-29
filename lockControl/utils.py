def danger_check_status(status):
    return status.get("lock") and not status.get("door")


