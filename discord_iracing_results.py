import iracing_results_scraper_env as app_env

import discord
from discord.ext import tasks, commands

from pyracing import client as pyracing

STATS_FORMAT = '**%s** (<@!%s>) just finished a race!\n**Series**: %s\n**Car**: %s\n**Track**: %s\n**SOF**: %s\n**Start**: %s\t**Finish**: %s'

bot = commands.Bot (command_prefix = '!', case_insensitive = True)

ir_client = pyracing.Client (app_env.IRACING_USER, app_env.IRACING_PASSWORD)

async def print_last_race_stats (channel_id, discord_id, iracing_id):
    try:
        channel = bot.get_channel (channel_id)
                
        last_race = await ir_client.last_races_stats (iracing_id)
        last_race = last_race[0]
        subsession_id = last_race.subsession_id       
             
        if app_env.iracer_to_session_map.get (iracing_id) == subsession_id:
            return
        
        driver_status = await ir_client.driver_status (iracing_id)
        
        last_series_list = await ir_client.last_series (iracing_id)                
        last_race_series_name = next ((last_series.series_name_short for last_series in last_series_list if last_series.series_id == last_race.series_id), 'Unknown')
        
        subession_data = await ir_client.subsession_data (subsession_id, iracing_id)
        car_class_id = subession_data.drivers[0].car_class_id
        
        car_class_data = await ir_client.car_class (car_class_id)
        car_name = next ((car_data.name for car_data in car_class_data.cars if car_data.id == subession_data.drivers[0].car_id), 'Unknown')
        
        await channel.send (STATS_FORMAT % (driver_status.name, discord_id, last_race_series_name, car_name, last_race.track, last_race.strength_of_field, last_race.pos_start, last_race.pos_finish))
        app_env.iracer_to_session_map[iracing_id] = subsession_id
    except:
        print ("Unexpected error happened during iRacing query")


@tasks.loop (seconds = app_env.REFRESH_RATE)
async def scrape_ir_results ():
    await bot.wait_until_ready ()  
    if not bot.is_closed ():
        app_env.load_iracer_to_session_map ()    
        for iracing_id, discord_id in app_env.iracers_to_query.items ():
            await print_last_race_stats (app_env.DISCORD_CHANNEL_ID, discord_id, iracing_id)
            
        app_env.save_iracer_to_session_map ()


@bot.command(name='subscribe', help='Subscribe given user to the result polling service')
async def subscribe(ctx, member_id = None, discord_id = None):
    if member_id is None:
        await ctx.send ('Please enter an iRacing member ID to subscribe')
        return
        
    if discord_id is None:
        discord_id = ctx.message.author.id
    else:
        discord_id = discord_id.replace("<","")
        discord_id = discord_id.replace(">","")
        discord_id = discord_id.replace("@","")
        discord_id = discord_id.replace("!","")
     
    iracing_id = member_id.strip ()
    try:
        iracing_id_int = int (iracing_id) # check if input is indeed integer
        app_env.iracers_to_query[iracing_id] = discord_id
        await ctx.send ('Subscribed <@!' + str (discord_id) + '>.')
    except ValueError:
        await ctx.send ('Failed to subscribe <@!' + str (discord_id) + '>. Wrong message format!')

    app_env.save_iracers_to_query ()


@bot.command(name='unsubscribe', help='Unubscribe given user from the result polling service')
async def unsubscribe(ctx, member_id = None):
    if member_id is None:
        await ctx.send ('Please enter an iRacing member ID to unsubscribe')
        return
     
    iracing_id = member_id.strip ()
    try:
        iracing_id_int = int (iracing_id) # check if input is indeed integer
        discord_id = app_env.iracers_to_query[iracing_id]
        del app_env.iracers_to_query[iracing_id]
        await ctx.send ('Unsubscribed <@!' + str (discord_id) + '>.')
    except ValueError:
        await ctx.send ('Failed to unsubscribe ' + str (iracing_id) + '. Wrong message format!')
    except IndexError:
        await ctx.send ('Failed to unsubscribe ' + str (iracing_id) + '. User is not subscribed!')
    except KeyError:
        await ctx.send ('Failed to unsubscribe ' + str (iracing_id) + '. User is not subscribed!')
    finally:
        try:
            del app_env.iracer_to_session_map[iracing_id]
        except:
            print ("No session data found to delete")

    app_env.save_iracers_to_query ()
    app_env.save_iracer_to_session_map ()


@bot.command(name='list', help='List all users that are subscribed to the polling service')
async def list(ctx):
    member_list = ""
    for iracing_id, discord_id in app_env.iracers_to_query.items ():
        discord_user = await bot.fetch_user(discord_id)
        member_list += ("%s - %s\n" % (iracing_id, discord_user.name))
        
    await ctx.send ('List of subscribed users:')
    await ctx.send (member_list)
 

@bot.event
async def on_ready ():
    print( f'Initialized as {bot.user} (ID: {bot.user.id})')
    
    app_env.load_iracers_to_query ()
    scrape_ir_results.start ()
    
bot.run (app_env.DISCORD_TOKEN)