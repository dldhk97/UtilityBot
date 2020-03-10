import discord
import asyncio
import re
import os
import sys
import environment
import datetime

from datetime import datetime
from discord.ext import commands
from message import Message, MessageType, BotEditType
from botexception import ExceptionType, BotException

bot = commands.Bot('')
bot_env = environment.BotEnv.instance()

EMBED_COLOR = 0xd6f9ff

IS_READY = False


@bot.event
async def on_ready(): #봇이 준비되었을 때 출력할 내용
    global IS_READY
    bot_env.set_env('BOT_ID', bot.user.id)

    print(bot.user.name)
    print(bot.user.id)

    await bot.change_presence(activity=discord.Game(name=f'{bot.command_prefix}도움'))

    print('Ready to go!')
    IS_READY = True


async def help(ctx):
    if not IS_READY:
        log(from_text(ctx), '봇이 아직 준비되지 않았습니다!')
        return

    log(from_text(ctx), '도움')
    embed = discord.Embed(title='유틸리티 봇입니다.',
                  description='자세한 기능은 아래를 참조하세요.',
                  color=EMBED_COLOR)
    USE_GAMIE_MODE = '(사용중)' if bot_env.get_env('USE_GAMIE_MODE') else '(비활성화)'
    USE_GAMIE_REACTION_MODE = '(사용중)' if bot_env.get_env('USE_GAMIE_REACTION_MODE') else '(비활성화)'
    USE_SPOILER_REACTION_MODE = '(사용중)' if bot_env.get_env('USE_SPOILER_REACTION_MODE') else '(비활성화)'

    GAMIE_EMOJI = bot_env.get_env('GAMIE_EMOJI')
    SPOILER_REACTION_EMOJI = bot_env.get_env('SPOILER_REACTION_EMOJI')
    UNSPOILER_REACTION_EMOJI = bot_env.get_env('UNSPOILER_REACTION_EMOJI')

    embed.add_field(name='개미옵션 ' + USE_GAMIE_MODE, value='개미, 미개한 메시지가 보이면 개미 이모지를 답니다.', inline=False)
    embed.add_field(name='개미 리액션 옵션 ' + USE_GAMIE_REACTION_MODE, value=f'메시지에 개미 이모지 {GAMIE_EMOJI} 가 달리면 동조합니다.', inline=False)
    embed.add_field(name='스포일러 리액션 옵션 ' + USE_SPOILER_REACTION_MODE, 
                    value='메시지에 스포일러 이모지 ' + SPOILER_REACTION_EMOJI + ' 가 달리면 메시지를 스포일러로 바꿉니다.\n' + \
                        '메시지에 언스포일러 이모지 ' + UNSPOILER_REACTION_EMOJI + ' 가 달리면 스포일러된 메시지를 공개합니다.\n' + \
                        '``` 혹은 > 같은 마크다운 텍스트는 지원하지 않습니다.\n',
                   inline=False)

    embed.set_footer(text='Embed 스포일러는 정상적으로 작동하지 않을 수 있습니다.')
    await ctx.channel.send(embed=embed)


@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    if ctx.content.startswith(f'{bot.command_prefix}도움'):
        await help(ctx)
        return
    elif ctx.content.startswith(f'{bot.command_prefix}이동'):
        await move_message(ctx)
        return

    if bot_env.get_env('USE_GAMIE_MODE') is True:
        if ('개미' in ctx.content) or ('미개' in ctx.content):
            if not IS_READY:
                log(from_text(ctx), '봇이 아직 준비되지 않았습니다!')
                return

            log(from_text(ctx), '개미 발견')
            await ctx.add_reaction(bot_env.get_env('GAMIE_EMOJI'))
            log(from_text(ctx), '개미 이모지 달았음')
            return


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    valid_emojies = get_valid_emojies()

    if reaction.emoji in valid_emojies:
        message = reaction.message
        emoji = reaction.emoji

        if bot_env.get_env('USE_GAMIE_REACTION_MODE') is True:
            if emoji == bot_env.get_env('GAMIE_EMOJI'):
                if not IS_READY:
                    log(from_text(ctx), '봇이 아직 준비되지 않았습니다!')
                    return
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

def get_valid_emojies():
    valid_emojies = []
    reaction_emojies = bot_env._reaction_emojies
    
    for key in reaction_emojies:
        e = bot_env.get_env(key)
        valid_emojies.append(e)

    return valid_emojies


@bot.event
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
                await message.remove_reaction(bot_env.get_env('GAMIE_EMOJI'), bot.user)
                log(from_text(message), '개미 이모지 삭제')
                return


async def spoiler_convert(is_spoiler, message, requester):
    if not IS_READY:
        log(from_text(ctx), '봇이 아직 준비되지 않았습니다!')
        return

    log(from_text(message), '메시지 변환 시작...')

    channel = message.channel

    is_mention = True if bot_env.get_env('SPOILER_MENTION') else False

    try:
        msg = Message(message)

        spoiled_msg = await msg.convert(is_spoiler, requester, is_mention)

        if msg._message_type in [MessageType.STRING, MessageType.EMBED_IMAGE, MessageType.EMBED_VIDEO]:
            await channel.send(spoiled_msg)

        elif msg._message_type is MessageType.ATTACHMENT:
            await channel.send(file=spoiled_msg._file, content=spoiled_msg._content)

        elif msg._message_type is MessageType.EMBED:
            await channel.send(embed=spoiled_msg)

        else:
            await channel.send('알 수 없는 메시지 타입입니다!')
            return

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

async def move_message(message):
    if not IS_READY:
        log(from_text(ctx), '봇이 아직 준비되지 않았습니다!')
        return

    log(from_text(message), '메시지 이동 시작...')

    

def from_text(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    
    channel_type = ctx.channel.type.value
    if channel_type == 1:
        return f'DM > {ctx.author.name}'

    else:
        return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'


def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')


@bot.event
async def on_command_error(ctx, error):
    log(from_text(ctx), error)
    await ctx.channel.send(error)

if __name__ == '__main__':
    try:
        environment.load_env()
        bot.command_prefix = bot_env.get_env('PREFIX')
        bot.run(bot_env.get_env('BOT_TOKEN'))
    except Exception as e:
        print('load env failed.', e)