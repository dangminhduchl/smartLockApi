def danger_check_status(status):
    print("!")
    return status.get("lock") and not status.get("door")


