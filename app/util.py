from shortuuid import ShortUUID


def random_string(length=16):
    return ShortUUID().random(length=length)
