import discord
import requests
import json
import asyncio
import time
import websockets
import os
from websocket._exceptions import WebSocketTimeoutException
from websocket import create_connection as create_connection
from discord import app_commands

# Check if the configuration file exists
if not os.path.exists('config.json'):
    # If not, create an empty one
    with open('config.json', 'w') as f:
        json.dump({}, f)

# Now, load the configuration
with open('config.json') as f:
    config = json.load(f)

panel_url = config.get("PTERODACTYL_PANEL_URL")
api_key = config.get("PTERODACTYL_API_KEY")

with open('token.json') as f:
    config = json.load(f)

bot_token = config["DISCORD_BOT_TOKEN"]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

bot_enabled = True
maintenance_message = "The bot is currently in maintenance mode."


@tree.command(
    name="setup",
    description="Setup the bot",
)
async def setup_command(interaction, panel_url: str, api_key: str, owner_id: str):
    config = {
        "PTERODACTYL_PANEL_URL": panel_url,
        "PTERODACTYL_API_KEY": api_key,
        "OWNER_ID": owner_id
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)
        embed = discord.Embed(title="Setup", description="Configuration saved successfully! Please reboot the bot!", color=discord.Color.from_rgb(67, 118, 116))
        embed.set_footer(text="RR by Tumba©")
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

@tree.command(
    name="toggle",
    description="Toggle the bot on or off",
)
async def toggle_command(interaction, message: str = None):
    global bot_enabled, maintenance_message

    # Load the configuration
    with open('config.json') as f:
        config = json.load(f)

    owner_id = config["OWNER_ID"]

    if str(interaction.user.id) == owner_id:
        bot_enabled = not bot_enabled
        status = "enabled" if bot_enabled else "disabled"
        if message:
            maintenance_message = message
        embed = discord.Embed(title=f"Bot {status}", description=f"{maintenance_message}", color=discord.Color.from_rgb(67, 118, 116))
        embed.set_footer(text="RR by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
    else:
        embed = discord.Embed(title="Error", description="You do not have permission to use this command.", color=discord.Color.red())
        embed.set_footer(text="RR by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

@tree.command(
    name="status",
    description="Check the status of the servers",
)
async def status_command(interaction):

    embed = discord.Embed(title="", description="Reading Status... ❗", color=discord.Color.from_rgb(67, 118, 116))
    embed.set_footer(text="PteroBot by Tumba©")
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=25)

    headers = {'Authorization': 'Bearer ' + api_key}
    response = requests.get(panel_url + '/api/application/servers', headers=headers)
    servers = response.json()

    # Create a new Discord embed
    embed = discord.Embed(title="Server Status", color=0x437674)

    for server in servers['data']:
        uuid = server['attributes']['identifier']

        # Make a request to the Pterodactyl API to fetch the server status using the UUID
        response = requests.get(panel_url + '/api/client/servers/' + uuid + '/resources', headers=headers)
        server_status = response.json()

        # Change the "running" status to "Online" and add "starting" status
        status = server_status['attributes']['current_state']
        if status == 'running':
            status = 'Online'
            emoji = '🟢'
        elif status == 'starting':
            emoji = '🟠'
        else:
            emoji = '🔴'

        # Add the server status to the Discord embed
        embed.add_field(name=server['attributes']['name'], value=emoji + ' ' + status, inline=False)

    embed.set_footer(text="PteroBot by Tumba©")

    original_response = await interaction.original_response()
    await original_response.edit(embed=embed)

@tree.command(
    name="start",
    description="Starts a specific server",
)
async def start_command(interaction: discord.Interaction, server_name: str):

    global bot_enabled, maintenance_message
    if not bot_enabled:
        embed = discord.Embed(title="❗ Bot disabled! ❗", color=discord.Color.from_rgb(67, 118, 116))
        embed.add_field(name="Reason", value=f"{maintenance_message}", inline=False)
        embed.add_field(name="Exempt commands", value="`/status`", inline=False)
        delete_time = int(time.time()) + 10  
        embed.add_field(name="", value=f"Deleting <t:{delete_time}:R> ❗", inline=False) 
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        return

    response = requests.get(f'{panel_url}/api/application/servers', headers={'Authorization': f'Bearer {api_key}'})
    servers = response.json()

    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'].lower() == server_name.lower():
            server_uuid = server['attributes']['uuid']
            break

    if server_uuid is None:
        embed = discord.Embed(title="ERROR", description=f"❗ No server found with the name **{server_name}**", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=3)
        return

    # Check the current server status
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/resources', headers={'Authorization': f'Bearer {api_key}'})
    server_status = response.json()['attributes']['current_state']

    if server_status == 'running':
        embed = discord.Embed(title="", description=f"Server {server_name} is already running ❗", color=discord.Color.yellow())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Send the start signal
    url = f'{panel_url}/api/client/servers/{server_uuid}/power'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    data = json.dumps({"signal": "start"})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        embed = discord.Embed(title="", description=f"Server {server_name} started successfully ✅", color=discord.Color.green())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    else:
        embed = discord.Embed(title="ERROR", description=f"❗ Failed to start server {server_name}", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

@tree.command(
    name="stop",
    description="Stops a specific server",
)
async def stop_command(interaction: discord.Interaction, server_name: str):

    global bot_enabled, maintenance_message
    if not bot_enabled:
        embed = discord.Embed(title="❗ Bot disabled! ❗", color=discord.Color.from_rgb(67, 118, 116))
        embed.add_field(name="Reason", value=f"{maintenance_message}", inline=False)
        embed.add_field(name="Exempt commands", value="`/status`", inline=False)
        delete_time = int(time.time()) + 10  
        embed.add_field(name="", value=f"Deleting <t:{delete_time}:R> ❗", inline=False) 
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        return
    
    response = requests.get(f'{panel_url}/api/application/servers', headers={'Authorization': f'Bearer {api_key}'})
    servers = response.json()

    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'].lower() == server_name.lower():
            server_uuid = server['attributes']['uuid']
            break

    if server_uuid is None:
        embed = discord.Embed(title="ERROR", description=f"❗ No server found with the name **{server_name}**", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=3)
        return

    # Check the current server status
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/resources', headers={'Authorization': f'Bearer {api_key}'})
    server_status = response.json()['attributes']['current_state']

    if server_status == 'offline':
        embed = discord.Embed(title="", description=f"Server {server_name} is already stopped ❗", color=discord.Color.yellow())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Send the stop signal
    url = f'{panel_url}/api/client/servers/{server_uuid}/power'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    data = json.dumps({"signal": "stop"})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        embed = discord.Embed(title="", description=f"Server {server_name} stopped successfully ✅", color=discord.Color.green())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    else:
        embed = discord.Embed(title="ERROR", description=f"❗ Failed to stop server {server_name}", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

@tree.command(
    name="restart",
    description="Restarts a specific server",
)
async def restart_command(interaction: discord.Interaction, server_name: str):

    global bot_enabled, maintenance_message
    if not bot_enabled:
        embed = discord.Embed(title="❗ Bot disabled! ❗", color=discord.Color.from_rgb(67, 118, 116))
        embed.add_field(name="Reason", value=f"{maintenance_message}", inline=False)
        embed.add_field(name="Exempt commands", value="`/status`", inline=False)
        delete_time = int(time.time()) + 10  
        embed.add_field(name="", value=f"Deleting <t:{delete_time}:R> ❗", inline=False) 
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        return

    response = requests.get(f'{panel_url}/api/application/servers', headers={'Authorization': f'Bearer {api_key}'})
    servers = response.json()

    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'].lower() == server_name.lower():
            server_uuid = server['attributes']['uuid']
            break

    if server_uuid is None:
        embed = discord.Embed(title="ERROR", description=f"❗ No server found with the name **{server_name}**", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=3)
        return

    # Check the current server status
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/resources', headers={'Authorization': f'Bearer {api_key}'})
    server_status = response.json()['attributes']['current_state']

    if server_status == 'offline':
        embed = discord.Embed(title="", description=f"Server {server_name} is not running, cannot restart", color=discord.Color.yellow())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return
    elif server_status == 'restarting':
        embed = discord.Embed(title="", description=f"Server {server_name} is already restarting ❗", color=discord.Color.yellow())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Send the restart signal
    url = f'{panel_url}/api/client/servers/{server_uuid}/power'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    data = json.dumps({"signal": "restart"})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        embed = discord.Embed(title="", description=f"Server {server_name} restarted successfully ✅", color=discord.Color.green())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    else:
        embed = discord.Embed(title="ERROR", description=f"❗ Failed to restart server {server_name}", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

@tree.command(
    name="kill",
    description="Kills a specific server",
)
async def kill_command(interaction: discord.Interaction, server_name: str):

    global bot_enabled, maintenance_message
    if not bot_enabled:
        embed = discord.Embed(title="❗ Bot disabled! ❗", color=discord.Color.from_rgb(67, 118, 116))
        embed.add_field(name="Reason", value=f"{maintenance_message}", inline=False)
        embed.add_field(name="Exempt commands", value="`/status`", inline=False)
        delete_time = int(time.time()) + 10  
        embed.add_field(name="", value=f"Deleting <t:{delete_time}:R> ❗", inline=False) 
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        return

    response = requests.get(f'{panel_url}/api/application/servers', headers={'Authorization': f'Bearer {api_key}'})
    servers = response.json()

    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'].lower() == server_name.lower():
            server_uuid = server['attributes']['uuid']
            break

    if server_uuid is None:
        embed = discord.Embed(title="ERROR", description=f"❗ No server found with the name **{server_name}**", color=discord.Color.red())
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=3)
        return

    # Check the current server status
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/resources', headers={'Authorization': f'Bearer {api_key}'})
    server_status = response.json()['attributes']['current_state']

    if server_status == 'offline':
        embed = discord.Embed(title="", description=f"Server {server_name} is already stopped ❗", color=discord.Color.yellow())
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return
    elif server_status == 'restarting':
        embed = discord.Embed(title="", description=f"Server {server_name} is currently restarting. Please wait until the process is complete before killing the server.", color=discord.Color.yellow())
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Send the kill signal
    url = f'{panel_url}/api/client/servers/{server_uuid}/power'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    data = json.dumps({"signal": "kill"})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        embed = discord.Embed(title="", description=f"Server {server_name} killed successfully ✅", color=discord.Color.green())
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    else:
        embed = discord.Embed(title="ERROR", description=f"❗ Failed to kill server **{server_name}**", color=discord.Color.red())
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

@tree.command(
    name="logs",
    description="Get server logs",
)
async def logs_command(interaction: discord.Interaction, server_name: str):

    global bot_enabled, maintenance_message
    if not bot_enabled:
        embed = discord.Embed(title="❗ Bot disabled! ❗", color=discord.Color.from_rgb(67, 118, 116))
        embed.add_field(name="Reason", value=f"{maintenance_message}", inline=False)
        embed.add_field(name="Exempt commands", value="`/status`", inline=False)
        delete_time = int(time.time()) + 10  
        embed.add_field(name="", value=f"Deleting <t:{delete_time}:R> ❗", inline=False) 
        embed.set_footer(text="PteroBot by Tumba©")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        return

    # Fetch the server UUIDs
    headers = {'Authorization': 'Bearer ' + api_key}
    response = requests.get(panel_url + '/api/application/servers', headers=headers)
    servers = response.json()

    # Find the server with the name that matches `server_name`
    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'] == server_name:
            server_uuid = server['attributes']['identifier']
            break

    if server_uuid is None:
        embed = discord.Embed(title="", description=f"No server found with the name {server_name} ❗", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")       
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Get the WebSocket token
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/websocket', headers=headers)
    data = response.json()
    token = data['data']['token']

    # Establish a WebSocket connection
    ws = await websockets.connect(data['data']['socket'])

    # Authenticate
    await ws.send(json.dumps({"event": "auth", "args": [token]}))

    # Request server logs
    await ws.send(json.dumps({"event":"send logs","args":[None]}))
    print("sent logs event")

    # Create an embed for the server logs
    embed = discord.Embed(title=f"{server_name} Logs", description="Fetching server logs... ❗", color=discord.Color.from_rgb(67, 118, 116))

    # Send the embed as a response to the logs command
    await interaction.response.send_message(embed=embed, ephemeral=False)

    # Start a new task that updates the embed every 2 seconds and stops after 15 seconds
    asyncio.create_task(update_logs(ws, interaction, server_name))

async def update_logs(ws, interaction, server_name):
    print("WebSocket connection established")  # Check 1
    original_response = await interaction.original_response()
    logs = []
    update_counter = 0

    start_time = time.time()
    while True:
        try:
            # Receive server logs
            result = await ws.recv()
            print(f"Received data: {result}")  # Check 2
            data = json.loads(result)

            # Check if the server is offline
            if data['event'] == 'status' and data['args'][0] == 'offline':
                # If the server is offline, close the WebSocket connection and delete the message
                await ws.close()
                print("Closed WebSocket connection because the server is offline.")

                # Inform the user that the server is offline
                delete_time = int(time.time()) + 5
                embed = discord.Embed(title="ERROR!", description=f"{server_name} **Server is offline**! ❗\nDeleting in <t:{delete_time}:R>", color=discord.Color.red())
                embed.set_footer(text="Powered by PteroBot by Tumba©")
                message = await original_response.edit(embed=embed)
                await asyncio.sleep(5)
                await message.delete()
                break

            # Only process data if the event is 'console output'
            if data['event'] == 'console output':
                logs.extend(data['args'])
                update_counter += 1

                # Update the embed every 5 log messages
                if update_counter % 4 == 0:
                    # Update the embed with the new logs
                    embed = discord.Embed(title=f"{server_name} Logs", color=discord.Color.from_rgb(67, 118, 116))
                    formatted_data = '\n'.join(logs[-5:])  # Only include the last 5 log messages
                    
                    # Ensure the formatted_data is not longer than 1024 characters
                    if len(formatted_data) > 1024:
                        # Cut off the start of the formatted_data to fit within the limit
                        formatted_data = '...' + formatted_data[-1021:]  # 3 dots + 1021 characters = 1024 characters

                    formatted_data = '```' + formatted_data + '```'
                    embed.add_field(name="Logs", value=formatted_data, inline=False)

                    embed.set_footer(text="PteroBot by Tumba©")
                    # Edit the original response with the updated embed
                    await original_response.edit(embed=embed)

            # If 20 seconds have passed, stop the task
            if time.time() - start_time > 20:
                ws.close()
                print("Closed WebSocket connection")
                await original_response.delete()  # Delete the message
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break
@tree.command(
    name="server",
    description="Get server stats"
)
async def server_command(interaction: discord.Interaction, server_name: str):
    # Fetch the server UUIDs
    headers = {'Authorization': 'Bearer ' + api_key}
    response = requests.get(panel_url + '/api/application/servers', headers=headers)
    servers = response.json()

    # Find the server with the name that matches `server_name`
    server_uuid = None
    for server in servers['data']:
        if server['attributes']['name'] == server_name:
            server_uuid = server['attributes']['identifier']
            break

    if server_uuid is None:
        embed = discord.Embed(title="", description=f"No server found with the name {server_name} ❗", color=discord.Color.red())
        embed.set_footer(text="Powered by PteroBot by Tumba©")       
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        return

    # Get the WebSocket token
    response = requests.get(f'{panel_url}/api/client/servers/{server_uuid}/websocket', headers=headers)
    data = response.json()
    token = data['data']['token']

    # Establish a WebSocket connection
    ws = create_connection(data['data']['socket'])

    # Authenticate
    ws.send(json.dumps({"event": "auth", "args": [token]}))

    # Request server stats
    ws.send(json.dumps({"event":"send stats","args":[None]}))
    print("sent stats event")

    # Create an embed for the server stats
    embed = discord.Embed(title=f"{server_name} Stats", description="Fetching server stats... ❗", color=0x00ff00)

    # Send the embed as a response to the server command
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=20) 

    # Start a new task that updates the embed every 2 seconds and stops after 15 seconds
    asyncio.create_task(update_message(ws, interaction, server_name))

async def update_message(ws, interaction, server_name):
    start_time = time.time()
    original_response = await interaction.original_response()
    while True:
        # Receive server stats
        result = ws.recv()
        data = json.loads(result)
        print(f"Received data: {result}")
        if data['event'] == 'stats':
            stats = json.loads(data['args'][0])

            # If the server is offline, stop the task
            if stats['state'] == 'offline':
                ws.close()
                print("Closed WebSocket connection because the server is offline.")
                delete_time = int(time.time()) + 15
                embed = discord.Embed(title="ERROR!", description=f"{server_name} **Server is offline**! ❗\nDeleting in <t:{delete_time}:R>", color=discord.Color.red())
                embed.set_footer(text="Powered by PteroBot by Tumba©")
                await original_response.edit(embed=embed)
                break

            # Update the embed with the new stats
            embed = discord.Embed(title=f"{server_name} Stats", color=discord.Color.from_rgb(67, 118, 116))

            # Add the server status to the Discord embed
            status = stats['state']
            if status == 'running':
                status = 'Online'
                emoji = '🟢'
            embed.add_field(name="Server Status", value=emoji + ' ' + status, inline=True)

            # Add the server resources to the Discord embed
            memory_mb = stats['memory_bytes'] / (1024 * 1024)  # Convert to MB
            cpu_usage = stats['cpu_absolute']
            disk_gb = stats['disk_bytes'] / (1024 * 1024 * 1024)  # Convert to GB
            network_rx_mb = stats['network']['rx_bytes'] / (1024 * 1024)  # Convert to MB
            network_tx_mb = stats['network']['tx_bytes'] / (1024 * 1024)  # Convert to MB
            uptime_hours = stats['uptime'] / 3600000  # Convert to hours

            embed.add_field(name="▫️ CPU Usage (%)", value=f"{cpu_usage:.1f}", inline=False)
            embed.add_field(name="▫️ Memory Usage (MB)", value=f"{memory_mb:.1f}", inline=False)
            embed.add_field(name="▫️ Disk Usage (GB)", value=f"{disk_gb:.1f}", inline=False)
            embed.add_field(name="▫️ Network Received (MB)", value=f"{network_rx_mb:.1f}", inline=False)
            embed.add_field(name="▫️ Network Transmitted (MB)", value=f"{network_tx_mb:.1f}", inline=False)
            embed.add_field(name="▫️ Uptime (hours)", value=f"{uptime_hours:.1f}", inline=False)

            embed.set_footer(text="PteroBot by Tumba©")
            # Edit the original response with the updated embed
            await original_response.edit(embed=embed)

        # If 15 seconds have passed, stop the task
        if time.time() - start_time > 15:
            ws.close()
            print("Closed WebSocket connection")
            await original_response.delete()  # Delete the message
            break

        # Wait for 2 seconds before the next update
        await asyncio.sleep(2)

@tree.command(
    name="about",
    description="Get information about the bot",
)
async def about_command(interaction):
    embed = discord.Embed(title="About", color=discord.Color.from_rgb(67, 118, 116))
    embed.add_field(name="Bot made by", value="Tumba", inline=True)
    embed.add_field(name="Python", value="[3.11.6](https://python.org)", inline=True)
    embed.add_field(name="discord.py", value="[2.3.2](https://discordpy.readthedocs.io/en/stable/)", inline=True)
    embed.add_field(name="PteroBot Version", value="[4.1](https://github.com/Tumba123/pterobot)", inline=False)
    embed.add_field(name="About RR", value="This bot has been made by Tumba with Python, its main purpose is to be a companion to your Pterodactyl Panel journey! The main features are /start,/stop,/restart and /kill (server name CASESensitve!) \n\n/status gives you a quick and dirty way to see what services are online/offline \n\n /server and /logs (server name) The server command let's you see real time resource usage! Logs are self explanatory, due to the limitation of websockets logs can only be displayed if they are being actively printed out. \n\nPlease do NOT rely on the logs command, if there are issues just go to your panel!. \n\nif you have any questions don't hesitate to contact me! support [discord](https://discord.gg/3qwqqA4GKF)!\n\n©Tumba or *TheRareGamer* (I go by two aliases) \n\nYes the bot profile picture is AI generated.", inline=False)
    embed.set_footer(text="PteroBot by Tumba©", icon_url="https://cdn.discordapp.com/avatars/1192093576327340135/81f1bb7a667e70b415346b429326cdc7.png")
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=30)

@client.event
async def on_ready():
    await tree.sync()
    print("Start")

client.run(bot_token)
