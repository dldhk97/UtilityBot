import os
import sys

from dotenv import load_dotenv

# TODO : 리눅스, win32 타겟별 세팅.
# TODO : 파이썬 버전별 세팅 3.5 ~ 3.8?

def load_env():
    load_dotenv()  # load bot environment

    bot_env = BotEnv.instance()

    bot_env.env_initialize('BOT_TOKEN')
    bot_env.env_initialize('PREFIX')

    bot_env.env_initialize('USE_GAMIE_MODE')
    bot_env.env_initialize('USE_GAMIE_REACTION_MODE')
    bot_env.env_initialize('USE_SPOILER_REACTION_MODE')

    bot_env.env_initialize('SPOILER_MENTION')

    bot_env.env_initialize('GAMIE_EMOJI', True)
    bot_env.env_initialize('SPOILER_REACTION_EMOJI', True)
    bot_env.env_initialize('UNSPOILER_REACTION_EMOJI', True)

    env_none_check('BOT_TOKEN', '봇 토큰이 없습니다.')
    env_none_check('PREFIX', 'PREFIX가 없습니다.')

    if bot_env.get_env('USE_GAMIE_MODE'):
        env_none_check('GAMIE_EMOJI', '개미 옵션이 켜져있지만, 개미 이모지가 설정되어있지 않습니다.')

    if bot_env.get_env('USE_GAMIE_REACTION_MODE'):
        env_none_check('GAMIE_EMOJI', '개미 리액션 옵션이 켜져있지만, 개미 이모지가 설정되어있지 않습니다.')
        bot_env._reaction_emojies.append('GAMIE_EMOJI')

    if bot_env.get_env('USE_SPOILER_REACTION_MODE'):
        env_none_check('SPOILER_REACTION_EMOJI', '스포일러 옵션이 켜져있지만, 스포일러 이모지가 설정되어있지 않습니다.')
        env_none_check('UNSPOILER_REACTION_EMOJI', '스포일러 옵션이 켜져있지만, 언스포일러 이모지가 설정되어있지 않습니다.')
        bot_env._reaction_emojies.append('SPOILER_REACTION_EMOJI')
        bot_env._reaction_emojies.append('UNSPOILER_REACTION_EMOJI')


def env_none_check(key, error_msg):
    if BotEnv.instance().get_env(key) is False:
        raise Exception(error_msg)


def emoji_convert(src):
    src = src.replace('+', '')

    if '1F' in src:
        src = '\\U000' + src[1:]
    else:
        src = '\\u' + src[1:]

    src = src.encode("latin_1").decode("raw_unicode_escape").encode('utf-16', 'surrogatepass').decode('utf-16')

    return src


class BotEnv():
    _instance = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    def __init__(self):
        self._env = {}
        self._reaction_emojies = []

    def set_env(self, key, value):
        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        self._env[key] = value

    # get env arg from .env file
    def env_initialize(self, key, is_emoji=False):
        arg = os.getenv(key)
        if is_emoji:
            arg = emoji_convert(arg)
        if arg is None:
            arg = False
        BotEnv.instance().set_env(key, arg)

    def get_env(self, key):
        return self._env[key]