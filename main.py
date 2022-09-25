import discord
import environment
import datetime

from datetime import datetime
from message import Message, MessageType, BotEditType
from botexception import ExceptionType, BotException

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot_env = environment.BotEnv.instance()

EMBED_COLOR = 0xd6f9ff

IS_READY = False


@client.event
async def on_ready(): #봇이 준비되었을 때 출력할 내용
    global IS_READY
    bot_env.set_env('BOT_ID', client.user.id)

    print(client.user.name)
    print(client.user.id)

    await client.change_presence(activity=discord.Game(name=f'{client.command_prefix}도움'))

    print('Ready to go!')
    IS_READY = True


async def cmd_help(ctx):
    if not IS_READY:
        raise BotException(ExceptionType.BOT_NOT_READY, True)

    log(from_text(ctx), '도움')
    embed = discord.Embed(title='유틸리티 봇입니다.',
                  description='자세한 기능은 아래를 참조하세요.',
                  color=EMBED_COLOR)

    PREFIX = str(client.command_prefix)
    
    USE_GAMIE_MODE = 'ON' if bot_env.get_env('USE_GAMIE_MODE') else 'OFF'
    USE_GAMIE_REACTION_MODE = 'ON' if bot_env.get_env('USE_GAMIE_REACTION_MODE') else 'OFF'
    GAMIE_EMOJI = bot_env.get_env('GAMIE_EMOJI')

    USE_SPOILER_REACTION_MODE = 'ON' if bot_env.get_env('USE_SPOILER_REACTION_MODE') else 'OFF'
    SPOILER_MENTION = 'ON' if bot_env.get_env('SPOILER_MENTION') else 'OFF'
    SPOILER_REACTION_EMOJI = bot_env.get_env('SPOILER_REACTION_EMOJI')
    UNSPOILER_REACTION_EMOJI = bot_env.get_env('UNSPOILER_REACTION_EMOJI')

    MOVE_MENTION = 'ON' if bot_env.get_env('MOVE_MENTION') else 'OFF'
    USE_IMPORTANT_CHANNEL_REACTION_MODE = 'ON' if bot_env.get_env('USE_IMPORTANT_CHANNEL_REACTION_MODE') else 'OFF'
    IMPORTANT_CHANNEL_ID = bot_env.get_env('IMPORTANT_CHANNEL_ID')
    IMPORTANT_CHANNEL_REACTION_EMOJI = bot_env.get_env('IMPORTANT_CHANNEL_REACTION_EMOJI')

    USE_TRASH_CHANNEL_REACTION_MODE = 'ON' if bot_env.get_env('USE_TRASH_CHANNEL_REACTION_MODE') else 'OFF'
    TRASH_CHANNEL_ID = bot_env.get_env('TRASH_CHANNEL_ID')
    TRASH_CHANNEL_REACTION_EMOJI = bot_env.get_env('TRASH_CHANNEL_REACTION_EMOJI')

    embed.add_field(name='스포일러 리액션 옵션-' + USE_SPOILER_REACTION_MODE + ' 멘션-' + SPOILER_MENTION, 
                    value='메시지에 스포일러 이모지 ' + SPOILER_REACTION_EMOJI + ' 가 달리면 메시지를 스포일러로 바꿉니다.\n' + \
                        '메시지에 언스포일러 이모지 ' + UNSPOILER_REACTION_EMOJI + ' 가 달리면 스포일러된 메시지를 공개합니다.\n' + \
                        '``` 혹은 > 같은 마크다운 텍스트는 지원하지 않습니다.\n',
                   inline=False)
    embed.add_field(name='중요 채널 리액션 옵션-' + USE_IMPORTANT_CHANNEL_REACTION_MODE + ' 멘션-' + MOVE_MENTION, 
                    value='메시지에 중요 이모지 ' + IMPORTANT_CHANNEL_REACTION_EMOJI + ' 를 달면 중요 채널로 이동시킵니다.\n' + \
                        '중요 채널 : ' +  f'<#{IMPORTANT_CHANNEL_ID}> (ID:' + IMPORTANT_CHANNEL_ID + ')',
                   inline=False)
    embed.add_field(name='휴지통 채널 리액션 옵션-' + USE_TRASH_CHANNEL_REACTION_MODE + ' 멘션-' + MOVE_MENTION, 
                    value='메시지에 휴지통 이모지 ' + TRASH_CHANNEL_REACTION_EMOJI + ' 를 달면 휴지통 채널로 이동시킵니다.\n' + \
                        '휴지통 채널 : ' +  f'<#{TRASH_CHANNEL_ID}> (ID:' + TRASH_CHANNEL_ID + ')',
                   inline=False)
    embed.add_field(name='메시지 스포일러', value=f'{PREFIX}스포일러 [메시지ID] 로 메시지를 명령어로 스포일러 혹은 언스포일러 처리 할 수 있습니다.\n(언스포일러는 {PREFIX}언스포일러 [메시지ID]', inline=False)
    embed.add_field(name='메시지 이동', value=f'{PREFIX}이동 [메시지ID] [채널ID] 로 메시지를 명령어로 채널간 이동시킬 수 있습니다.', inline=False)
    embed.add_field(name='개미옵션-' + USE_GAMIE_MODE, value='개미, 미개한 메시지가 보이면 개미 이모지를 답니다.', inline=False)
    embed.add_field(name='개미 리액션 옵션-' + USE_GAMIE_REACTION_MODE, value=f'메시지에 개미 이모지 {GAMIE_EMOJI} 가 달리면 동조합니다.', inline=False)

    embed.set_footer(text='Embed 스포일러는 정상적으로 작동하지 않을 수 있습니다.')
    await ctx.channel.send(embed=embed)


@client.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    try:
        if ctx.content.startswith(f'{client.command_prefix}도움'):
            await cmd_help(ctx)
            return
        elif ctx.content.startswith(f'{client.command_prefix}이동'):
            await cmd_move_message(ctx)
            return
        elif ctx.content.startswith(f'{client.command_prefix}스포일러'):
            await cmd_spoiler_convert(ctx, True)
            return
        elif ctx.content.startswith(f'{client.command_prefix}언스포일러'):
            await cmd_spoiler_convert(ctx, False)
            return

        if bot_env.get_env('USE_GAMIE_MODE') is True:
            if ('개미' in ctx.content) or ('미개' in ctx.content):
                if not IS_READY:
                    raise BotException(ExceptionType.BOT_NOT_READY)

                log(from_text(ctx), '개미 발견')
                await ctx.add_reaction(bot_env.get_env('GAMIE_EMOJI'))
                log(from_text(ctx), '개미 이모지 달았음')
                return

    except BotException as be:
        log(from_text(ctx), be)
        if be._notice:
            await ctx.channel.send(be._reason)
    except Exception as e:
        log(from_text(ctx), e)
        await ctx.channel.send(e)


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if not IS_READY:
        raise BotException(ExceptionType.BOT_NOT_READY, True)

    emoji = reaction.emoji
    target_emoji = None

    for ve in get_valid_emojies():
        if ve.encode('unicode-escape') in emoji.encode('unicode-escape'):
            target_emoji = ve
            break

    if target_emoji:
        message = reaction.message
        emoji = target_emoji

        if bot_env.get_env('USE_GAMIE_REACTION_MODE') is True:
            if emoji == bot_env.get_env('GAMIE_EMOJI'):
                if not IS_READY:
                    raise BotException(ExceptionType.BOT_NOT_READY)
                log(from_text(message), '개미 이모지 발견')
                await message.add_reaction(bot_env.get_env('GAMIE_EMOJI'))
                return
        
        if bot_env.get_env('USE_SPOILER_REACTION_MODE') is True:
            if emoji == bot_env.get_env('SPOILER_REACTION_EMOJI'):
                log(from_text(message), '스포일러 이모지 발견')
                await spoiler_convert(True, message, user)
                return
            elif emoji == bot_env.get_env('UNSPOILER_REACTION_EMOJI'):
                log(from_text(message), '언스포일러 이모지 발견')
                await spoiler_convert(False, message, user)
                return

        if bot_env.get_env('USE_IMPORTANT_CHANNEL_REACTION_MODE') is True:
            if emoji == bot_env.get_env('IMPORTANT_CHANNEL_REACTION_EMOJI'):
                log(from_text(message), '중요 채널 이모지 발견')
                channel_id = bot_env.get_env('IMPORTANT_CHANNEL_ID')
                await move_message(message, channel_id)
                return

        if bot_env.get_env('USE_TRASH_CHANNEL_REACTION_MODE') is True:
            if emoji == bot_env.get_env('TRASH_CHANNEL_REACTION_EMOJI'):
                log(from_text(message), '휴지통 채널 이모지 발견')
                channel_id = bot_env.get_env('TRASH_CHANNEL_ID')
                await move_message(message, channel_id)
                return


def get_valid_emojies():
    valid_emojies = []
    reaction_emojies = bot_env._reaction_emojies
    
    for key in reaction_emojies:
        e = bot_env.get_env(key)
        valid_emojies.append(e)

    return valid_emojies


@client.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    valid_emojies = get_valid_emojies()

    if reaction.emoji in valid_emojies:
        message = reaction.message
        emoji = reaction.emoji

        if bot_env.get_env('USE_GAMIE_REACTION_MODE') is True:
            if emoji == bot_env.get_env('GAMIE_EMOJI'):
                log(from_text(message), '개미 이모지 삭제 발견')
                if '개미' in message.content or '미개' in message.content:
                    return
                await message.remove_reaction(bot_env.get_env('GAMIE_EMOJI'), client.user)
                log(from_text(message), '개미 이모지 삭제')
                return


async def spoiler_convert(is_spoiler, message, requester):
    if not IS_READY:
        raise BotException(ExceptionType.BOT_NOT_READY, True)

    log(from_text(message), '메시지 변환 시작...')

    channel = message.channel

    await channel.typing()                          # 봇 상태를 타이핑중으로 변경.

    is_mention = bot_env.get_env('SPOILER_MENTION')

    try:
        msg = Message(message)
        if is_spoiler:
            if msg._bot_edited_type is BotEditType.SPOILED:
                raise BotException(ExceptionType.ALREADY_SPOILER)
        else:
            if msg._bot_edited_type is BotEditType.UNSPOILED:
                raise BotException(ExceptionType.ALREADY_SPOILER)

        if is_spoiler:
            bot_edit_type = BotEditType.SPOILED
        else:
            bot_edit_type = BotEditType.UNSPOILED

        # extract header & content from message obj
        header, content = await msg.split_header(requester, is_mention)
        header = str(bot_edit_type) + ' ' + header
        edited_msg = await msg.edit(is_spoiler, header, content)
        
        await send_edited(channel, msg._message_type, edited_msg)

    except BotException as be:
        if be._exception_type in [ExceptionType.ALREADY_SPOILER, ExceptionType.ALREADY_UNSPOILER]:
            log(from_text(message), be)
        else:
            await channel.send(be)
    except Exception as e:
        await channel.send(e)
    else:
        try:
            await message.delete()
        except:
            log(from_text(message), '기존 메시지 삭제 실패')
        log(from_text(message), '메시지 변환 완료')


async def move_message(message, target_channel_id):
    log(from_text(message), '메시지 이동 시작...')

    is_mention = bot_env.get_env('MOVE_MENTION')

    try:
        msg = Message(message)
        header, content = await msg.split_header(message.author, is_mention)
        header = str(BotEditType.MOVED) + ' ' + header
        edited_message = await msg.edit(False, header, content)
        target_channel = await client.fetch_channel(target_channel_id)
        await send_edited(target_channel, msg._message_type, edited_message)
    except Exception as e:
        if e.code == 50001:
            e = '해당 채널에 접근할 수 없습니다.'
        elif e.code == 50035:
            e = '알 수 없는 채널입니다.'
        log(from_text(message), e)
        await message.channel.send(e)
    else:
        try:
            await message.delete()
        except:
            log(from_text(message), '기존 메시지 삭제 실패')
        log(from_text(message), '메시지 이동 완료')


async def send_edited(channel, message_type, edited_msg):
    if message_type in [MessageType.STRING, MessageType.EMBED_IMAGE, MessageType.EMBED_VIDEO]:
        await channel.send(edited_msg)

    elif message_type is MessageType.ATTACHMENT:
        await channel.send(file=edited_msg._file, content=edited_msg._content)

    elif message_type is MessageType.EMBED:
        await channel.send(embed=edited_msg)

    else:
        await channel.send('알 수 없는 메시지 타입입니다!')
        return

async def cmd_move_message(ctx):
    if not IS_READY:
        raise BotException(ExceptionType.BOT_NOT_READY, True)

    args = ctx.content.split(' ')
    if len(args) <= 2:
        raise BotException(ExceptionType.WRONG_COMMAND_ARGS, True, f'사용법 : {client.command_prefix}이동 [메시지ID] [채널]')

    message_id = args[1]
    channel_id = args[2]

    if channel_id.startswith('<#') and channel_id.endswith('>'):
        channel_id = channel_id[2:-1]

    try:
        message = await ctx.channel.fetch_message(message_id)
        await move_message(message, channel_id)
    except Exception as e:
        if e.code == 10008:
            e = '메시지가 탐색되지 않았습니다.'
        elif e.code == 50001:
            e = '해당 채널에 접근할 수 없습니다.'
        elif e.code == 50035:
            e = '채널ID 혹은 메시지 ID가 올바르지 않습니다.'
        log(from_text(ctx), e)
        await ctx.channel.send(e)

    return


async def cmd_spoiler_convert(ctx, is_spoiler):
    if not IS_READY:
        raise BotException(ExceptionType.BOT_NOT_READY, True)

    args = ctx.content.split(' ')
    if len(args) <= 1:
        raise BotException(ExceptionType.WRONG_COMMAND_ARGS, True, f'사용법 : {client.command_prefix}[스포일러|언스포일러] [메시지ID]')

    message_id = args[1]

    try:
        message = await ctx.channel.fetch_message(message_id)
        await spoiler_convert(is_spoiler, message, ctx.author)
    except Exception as e:
        if e.code == 10008:
            e = '메시지가 탐색되지 않았습니다.'
        if e.code == 50001:
            e = '해당 채널에 접근할 수 없습니다.'
        elif e.code == 50035:
            e = '메시지 ID가 올바르지 않습니다.'
        log(from_text(ctx), e)
        await ctx.channel.send(e)

    return

    
def from_text(ctx):
    channel_type = ctx.channel.type.value
    if channel_type == 1:
        return f'DM > {ctx.author.name}'

    else:
        return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'


def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')

@client.event
async def on_command_error(ctx, error):
    log(from_text(ctx), error)
    await ctx.channel.send(error)


if __name__ == '__main__':
    try:
        environment.load_env()
        client.command_prefix = bot_env.get_env('PREFIX')
        client.run(bot_env.get_env('BOT_TOKEN'))
    except Exception as e:
        print('.env 파일을 읽어 오는 중 오류가 발생하였습니다.\n원인 : ',e)