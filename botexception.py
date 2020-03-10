import enum

class ExceptionType(enum.Enum):
    ALREADY_SPOILER = 0
    ALREADY_UNSPOILER = 1
    WRONG_COMMAND = 2
    WRONG_COMMAND_ARGS = 3
    BOT_NOT_READY = 4
    PERMISSION_DENIED = 5

    UNKNOWN = -1

    def __str__(self):
        if self is ExceptionType.ALREADY_SPOILER:
            return 'ALREADY_SPOILER : '
        elif self is ExceptionType.ALREADY_UNSPOILER:
            return 'ALREADY_UNSPOILER : '
        elif self is ExceptionType.WRONG_COMMAND:
            return 'WRONG_COMMAND : '
        elif self is ExceptionType.WRONG_COMMAND_ARGS:
            return 'WRONG_COMMAND_ARGS : '
        elif self is ExceptionType.BOT_NOT_READY:
            return 'BOT_NOT_READY : '
        elif self is ExceptionType.PERMISSION_DENIED:
            return 'PERMISSION_DENIED : '
        else:
            return 'UNKNOWN : '

class BotException(Exception):
    

    def __init__(self, exception_type, notice=False, reason=None):
        self._exception_type = exception_type
        self._notice = notice
        if reason is None:
            self._reason = self.default_reason()
        else:
            self._reason = reason

    def __str__(self):
        return str(self._exception_type) + self._reason


    def default_reason(self):
        if self._exception_type is ExceptionType.ALREADY_SPOILER:
            return '이미 스포일러화 되어있습니다.'
        elif self._exception_type is ExceptionType.ALREADY_UNSPOILER:
            return '이미 언스포일러화 되어있습니다.'
        elif self._exception_type is ExceptionType.WRONG_COMMAND:
            return '존재하지 않는 명령어 입니다.'
        elif self._exception_type is ExceptionType.WRONG_COMMAND_ARGS:
            return '명령어 인자가 올바르지 않습니다.'
        elif self._exception_type is ExceptionType.BOT_NOT_READY:
            return '봇이 아직 준비되지 않았습니다.'
        elif self._exception_type is ExceptionType.PERMISSION_DENIED:
            return '권한이 없습니다.'
        else:
            return '알 수 없는 오류입니다.'