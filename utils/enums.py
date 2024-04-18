from enum import Enum


class FocusAreaEnum(Enum):
    AEROBIC = "유산소"
    CHEST = "가슴"
    BACK = "등"
    SHOULDER = "어깨"
    ARM = "팔"
    LOWER_BODY = "하체"
    CORE = "코어"

    @classmethod
    def choices(cls):
        return [(member.name, member.value) for member in cls]
