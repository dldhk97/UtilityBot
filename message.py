import enum
import datetime
import re
import environment

from pytz import timezone, utc
from botexception import ExceptionType, BotException

KST = timezone('Asia/Seoul')

bot_env = environment.BotEnv.instance()

class MessageType(enum.Enum):
    STRING = 0
    ATTACHMENT = 1
    EMBED = 2
    EMBED_IMAGE = 3
    EMBED_VIDEO = 4


class BotEditType(enum.Enum):
    NOT_EDITED = 0
    SPOILED = 1
    UNSPOILED = 2
    MOVED = 3

    def check_type(message):
        if message.author.id is bot_env.get_env('BOT_ID'):
            if message.content.startswith('Spoiled By'):
                return BotEditType.SPOILED
            elif message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('Spoiled By'):
                return BotEditType.SPOILED
            elif message.content.startswith('Unspoiled By'):
                return BotEditType.UNSPOILED
            elif message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('Unspoiled By'):
                return BotEditType.UNSPOILED
            elif message.content.startswith('Moved By'):
                return BotEditType.MOVED
            elif message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('Moved By'):
                return BotEditType.MOVED
        return BotEditType.NOT_EDITED

    def __str__(self):
        if self is BotEditType.SPOILED:
            return 'Spoiled By'
        elif self is BotEditType.UNSPOILED:
            return 'Unspoiled By'
        elif self is BotEditType.MOVED:
            return 'Moved By'
        else:
            return ''


class Attachment:

    def __init__(self, file, content):
        self._file = file
        self._content = content

class Message:

    def __init__(self, message):
        self._message = message
        self._message_type = self._judge_type(message)
        date = message.created_at.astimezone(KST)
        self._date_str = str(date.strftime("%Y-%m-%d %H:%M"))
        self._bot_edited_type = BotEditType.check_type(message)


    async def split_header(self, requester, is_mention=False):
        # EMBED인지 체크하고 content 결정
        if self._message_type is MessageType.EMBED:
            content = self._message.embeds[0].title
            requester_tag = requester.name
        else:
            content = self._message.content
            requester_tag = '<@' + str(requester.id) + '>' if is_mention else requester.name

        # 봇이 수정한 것이라면 원본 태그 분리
        if self._bot_edited_type is not BotEditType.NOT_EDITED:
            org_tag, content = self._split_orginal_tag(content)
        else:
            if self._message_type is MessageType.EMBED:
                org_str = self._message.author.name
            else:
                org_str = '<@' + str(self._message.author.id) + '> ' if is_mention else self._message.author.name
            org_tag = org_str + ' ' + self._date_str
                
        header = requester_tag +'\n' + org_tag + '\n'

        return header, content


    async def edit(self, is_spoiler, header, content):

        if is_spoiler:
            spoiler_symbol = '||'
        else:
            spoiler_symbol = ''

        if self._message_type is MessageType.STRING:
            url = self._parse_url(content)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + ' ')
            if content:
                content = spoiler_symbol + self._str_unspoil(content) + spoiler_symbol
            return header + content

        elif self._message_type is MessageType.ATTACHMENT:
            attach = self._message.attachments[0]
            file = await attach.to_file()
            file = self._convert_file_name(is_spoiler, file)
            if content:
                content = spoiler_symbol + self._str_unspoil(content) + spoiler_symbol
            return Attachment(file, header + content)

        elif self._message_type is MessageType.EMBED:
            embed = self._message.embeds[0]
            embed.title = header + spoiler_symbol + self._str_unspoil(content) + spoiler_symbol
            embed.description = spoiler_symbol + self._str_unspoil(embed.description) + spoiler_symbol
            
            c = 0
            for f in embed.fields:
                n = spoiler_symbol + self._str_unspoil(f.name) + spoiler_symbol
                v = spoiler_symbol + self._str_unspoil(f.value) + spoiler_symbol
                embed.set_field_at(c, name=n, value=v, inline=f.inline)
                c += 1

            if embed.footer:
                footer_str = spoiler_symbol + self._str_unspoil(embed.footer.text) + spoiler_symbol
                embed.add_field(name='footer', value=footer_str, inline=False)
                embed.set_footer(text='')
            return embed

        elif self._message_type in [MessageType.EMBED_IMAGE, MessageType.EMBED_VIDEO]:
            embed = self._message.embeds[0]
            if content:
                content = content.replace(embed.url, embed.url + ' ')
                content = spoiler_symbol + self._str_unspoil(content) + spoiler_symbol
            return header + content


    def _split_orginal_tag(self, content):
        content = self._delete_requester_tag(content)    # 요청자 태그는 없앤다.
        splited = content.split('\n',1)
        try:
            org_tag = splited[0]                        # 원본 정보 태그는 그대로 쓴다.
            content = splited[1]                        # 원본 내용 추출
        except IndexError:
            content = ''

        return org_tag, content


    def _judge_type(self, message):
        if message.attachments:
            return MessageType.ATTACHMENT

        elif message.embeds:
            if message.embeds[0].type == 'image':
                return MessageType.EMBED_IMAGE
            elif message.embeds[0].type == 'video':
                return MessageType.EMBED_VIDEO
            return MessageType.EMBED

        else:
            return MessageType.STRING

    def _convert_file_name(self, is_spoiler, file):
        if is_spoiler:
            if not file.filename.startswith('SPOILER_'):
                file.filename = 'SPOILER_' + file.filename
        else:
            if file.filename.startswith('SPOILER_'):
                file.filename = file.filename.replace('SPOILER_', '')

        return file


    def _parse_url(self, str):
        if str:
            return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
        else:
            return


    def _delete_requester_tag(self, content):
        c = content.split('\n',1)
        if len(c) > 1:
            return c[1]
        else:
            return ''


    def _str_unspoil(self, str):
        c = str.count('||')

        if c == 0:
            return str
        elif c % 2 == 0:
            return str.replace('||', '', c)
        else:
            str = str.replace('||', '', c - 1)
            return str.replace('||', '| | ', 1)