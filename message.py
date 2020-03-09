import enum
import datetime
import re

from pytz import timezone, utc

KST = timezone('Asia/Seoul')

class MessageType(enum.Enum):
    STRING = 0
    ATTACHMENT = 1
    EMBED = 2
    EMBED_IMAGE = 3
    EMBED_VIDEO = 4


class BotEditType(enum.Enum):
    NONE = 0
    SPOILED = 1
    UNSPOILED = 2

    def check_type(message):
        if message.content.startswith('Spoiled By'):
            return BotEditType.SPOILED
        elif message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('Spoiled By'):
            return BotEditType.SPOILED
        elif message.content.startswith('Unspoiled By'):
            return BotEditType.UNSPOILED
        elif message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('Unspoiled By'):
            return BotEditType.UNSPOILED
        else:
            return BotEditType.NONE


class Attachment:

    def __init__(self, file, content):
        self._file = file
        self._content = content

class Message:

    def __init__(self, message):
        self._message = message
        self._message_type = self.judge_type(message)

        date = utc.localize(message.created_at).astimezone(KST)
        self._date_str = str(date.strftime("%Y-%m-%d %H:%M"))


    async def to_spoiler(self, requester, bot_edit_type=BotEditType.NONE, is_mention=False):
        if self._message_type is MessageType.EMBED:
            requester_tag = 'Spoiled By ' + requester.name
            org_tag = self._message.author.name + ' ' + self._date_str
            content = self._message.embeds[0].title
        else:
            if is_mention:
                requester_tag = 'Spoiled By <@' + str(requester.id) + '>'
                org_tag = '<@' + str(self._message.author.id) + '> ' + self._date_str
            else:
                requester_tag = 'Spoiled By ' + requester.name
                org_tag = self._message.author.name + ' ' + self._date_str
            content = self._message.content

        # 봇에 의해 스포일러 되거나 언스포일 된 것
        if bot_edit_type is not BotEditType.NONE:
            content = self.delete_requester_tag(content)    # 요청자 태그는 없앤다.
            splited = content.split('\n',1)
            try:
                org_tag = splited[0]                        # 원본 정보 태그는 그대로 쓴다.
                content = splited[1]                        # 원본 내용 추출
            except IndexError:
                content = ''

        header = requester_tag +'\n' + org_tag + '\n'
        if content:
            content = self.str_unspoil(content)

        if self._message_type is MessageType.STRING:
            url = self.parse_url(content)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + ' ')
            if content:
                content = '||' + content + '||'
            return header + content

        elif self._message_type is MessageType.ATTACHMENT:
            attach = self._message.attachments[0]
            file = await attach.to_file()
            file = self.make_file_spoiler(file)
            if content:
                content = '||' + content + '||'
            content = header + content
            return Attachment(file, content)

        elif self._message_type is MessageType.EMBED:
            embed = self._message.embeds[0]
            embed.title = header + '||' + content + '||'
            embed.description = '||' + embed.description + '||'

            url = self.parse_url(embed.url)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + ' ')
            
            c = 0
            for f in embed.fields:
                n = '||' + f.name + '||'
                v = '||' + f.value + '||'
                embed.set_field_at(c, name=n, value=v, inline=f.inline)
                c += 1

            if embed.footer:
                embed.add_field(name='footer', value='||' + embed.footer.text + '||', inline=False)                 # footer spoiler
                embed.set_footer(text='')
            return embed

        elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
            embed = self._message.embeds[0]
            content = content.replace(embed.url, embed.url + ' ')
            if content:
                content = '||' + content + '||'
            return header + content


    async def to_unspoiler(self, requester, bot_edit_type=BotEditType.NONE, is_mention=False):
        if self._message_type is MessageType.EMBED:
            requester_tag = 'Unspoiled By ' + requester.name
            org_tag = self._message.author.name + ' ' + self._date_str
            content = self._message.embeds[0].title
        else:
            if is_mention:
                requester_tag = 'Unspoiled By <@' + str(requester.id) + '>'
                org_tag = '<@' + str(self._message.author.id) + '> ' + self._date_str
            else:
                requester_tag = 'Unspoiled By ' + requester.name
                org_tag = self._message.author.name + ' ' + self._date_str
            content = self._message.content

        # 봇에 의해 스포일러 되거나 언스포일 된 것
        if bot_edit_type is not BotEditType.NONE:
            content = self.delete_requester_tag(content)    # 요청자 태그는 없앤다.
            splited = content.split('\n',1)
            try:
                org_tag = splited[0]                        # 원본 정보 태그는 그대로 쓴다.
                content = splited[1]                        # 원본 내용 추출
            except IndexError:
                content = ''

        header = requester_tag +'\n' + org_tag + '\n'
        if content:
            content = self.str_unspoil(content)

        if self._message_type is MessageType.STRING:
            url = self.parse_url(content)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + ' ')

            return header + content

        elif self._message_type is MessageType.ATTACHMENT:
            attach = self._message.attachments[0]
            file = await attach.to_file()
            file = self.make_file_unspoiler(file)
            content = header + content
            return Attachment(file, content)

        elif self._message_type is MessageType.EMBED:
            embed = self._message.embeds[0]
            embed.title = header + content
            embed.description = embed.description.replace('||', '')

            url = self.parse_url(embed.url)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + ' ')
            
            c = 0
            for f in embed.fields:
                n = f.name.replace('||', '')
                v = f.value.replace('||', '')
                embed.set_field_at(c, name=n, value=v, inline=f.inline)
                c += 1

            if embed.footer:
                embed.add_field(name='footer', value=embed.footer.text.replace('||', ''), inline=False)                 # footer spoiler
                embed.set_footer(text='')
            return embed

        elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
            embed = self._message.embeds[0]
            content = content.replace(embed.url, embed.url + ' ')
            return header + content


    def judge_type(self, message):
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


    def make_file_spoiler(self, file):
        if not file.filename.startswith('SPOILER_'):
            file.filename = 'SPOILER_' + file.filename
        return file


    def make_file_unspoiler(self, file):
        if file.filename.startswith('SPOILER_'):
            file.filename = file.filename.replace('SPOILER_', '')
        return file


    def parse_url(self, str):
        if str:
            return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
        else:
            return


    def delete_requester_tag(self, content):
        c = content.split('\n',1)
        if len(c) > 1:
            return c[1]
        else:
            return ''

    def str_unspoil(self, str):
        c = str.count('||')

        if c == 0:
            return str
        elif c % 2 == 0:
            return str.replace('||', '', c)
        else:
            str = str.replace('||', '', c - 1)
            return str.replace('||', '| | ', 1)