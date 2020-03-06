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
        self._sender_metion = '<@' + str(message.author.id) + '>'


    async def to_spoiler(self, requester, spoiled_by_bot=False):
        requester_tag = 'Spoiled By <@' + str(requester.id) + '>\n'
        org_tag = self._sender_metion + ' ' + self._date_str + '\n'
        content = self._message.content

        # 봇에 의해 스포일러된 것이면, 이전 스포일러 요청자 삭제
        if spoiled_by_bot:
            content = self.delete_requester_tag(content)
            org_tag = ''
            if self._message_type is MessageType.STRING:
                return requester_tag + content

            elif self._message_type is MessageType.EMBED:
                embed = self._message.embeds[0]
                requester_tag = 'Spoiled By ' + requester.name + '\n'
                embed.title = requester_tag + self.delete_requester_tag(embed.title)
                return embed

            elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
                return requester_tag + content

        if self._message_type is MessageType.STRING:
            url = self.parse_url(content)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
            if url:
                content = content.replace(url[0], url[0] + '\n')

            if content.startswith('||') and content.endswith('||'):
                content = content[2:-2]

            return requester_tag + org_tag + '||' + content + '||'

        elif self._message_type is MessageType.ATTACHMENT:
            attach = self._message.attachments[0]
            file = await attach.to_file()
            file = await self.make_file_spoiler(file)
            return Attachment(file, requester_tag + org_tag  + content)

        elif self._message_type is MessageType.EMBED:
            requester_tag = 'Spoiled By ' + requester.name + '\n'
            org_tag = self._message.author.name + ' ' + self._date_str + '\n'
            embed = self._message.embeds[0]
            embed.title = requester_tag + org_tag + '||' + embed.title + '||'
            embed.description = '||' + embed.description + '||'
            c = 0

            for f in embed.fields:
                n = '||' + f.name + '||'
                v = '||' + f.value + '||'
                embed.set_field_at(c, name=n, value=v, inline=f.inline)
                c += 1
            embed.add_field(name='footer', value='||' + embed.footer.text + '||', inline=False)                 # footer spoiler
            embed.set_footer(text='')
            return embed

        elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
            embed = self._message.embeds[0]
            content = self.content_normalization(self._message.content)
            content = content.replace(embed.url, embed.url + '\n')
            content = '||' + content + '||'
            return requester_tag + org_tag + content


    async def to_unspoiler(self, requester, spoiled_by_bot):
        print('WA!')
        #header = 'Spoiled By <@' + str(requester.id) + '>\n' + self._sender_metion + ' ' + self._date_str + '\n'

        #if spoiled_by_bot:
        #    if self._message_type is MessageType.STRING:
        #        return self._message.content[2:-2]
        #    elif self._message_type is MessageType.ATTACHMENT:
        #        header = ''
        #    elif self._message_type is MessageType.EMBED:
        #        return self._message.embeds[0]
        #    elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
        #        return self._message.content

        #if self._message_type is MessageType.STRING:
        #    content = self.content_normalization(self._message.content)

        #    url = self.parse_url(content)                                   # 컨텐츠 안에 URL 있으면 따로 처리해줌.
        #    if url:
        #        content = content.replace(url[0], url[0] + '\n')

        #    if content.startswith('||') and content.endswith('||'):
        #        content = content[2:-2]

        #    return header + '||' + content + '||'

        #elif self._message_type is MessageType.ATTACHMENT:
        #    attach = self._message.attachments[0]
        #    content = self._message.content
        #    file = await attach.to_file()
        #    file = await self.make_file_spoiler(file)
        #    return Attachment(file, header + content)

        #elif self._message_type is MessageType.EMBED:
        #    header = 'Spoiled By ' + requester.name + '\n' + self._message.author.name + ' ' + self._date_str + '\n'
        #    embed = self._message.embeds[0]
        #    embed.title = header + '||' + embed.title + '||'
        #    embed.description = '||' + embed.description + '||'
        #    c = 0
        #    for f in embed.fields:
        #        n = '||' + f.name + '||'
        #        v = '||' + f.value + '||'
        #        embed.set_field_at(c, name=n, value=v, inline=f.inline)
        #        c += 1
        #    embed.add_field(name='footer', value='||' + embed.footer.text + '||', inline=False)                 # footer spoiler
        #    return embed

        #elif self._message_type is MessageType.EMBED_IMAGE or self._message_type is MessageType.EMBED_VIDEO:
        #    embed = self._message.embeds[0]
        #    content = self.content_normalization(self._message.content)
        #    content = content.replace(embed.url, embed.url + '\n')
        #    content = '||' + content + '||'
        #    return header + content


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


    async def make_file_spoiler(self, file):
        if not file.filename.startswith('SPOILER_'):
            file.filename = 'SPOILER_' + file.filename
        return file

    def parse_url(self, str):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)


    def content_normalization(self, content):
        #if '> ' in content:
        #    content = content.replace('> ', '')
        #if '```' in content:
        #    content = content.replace('```', '')
        if '||' in content:
            content = content.replace('||', '')
        return content

    def delete_requester_tag(self, content):
        c = content.split('\n',1)
        if len(c) > 1:
            return c[1]
        else:
            return ''