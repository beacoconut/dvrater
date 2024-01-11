# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient
from telethon import events
import pandas as pd
import os
from telethon.tl.types import MessageMediaPhoto
import uuid
import numpy as np

# Saving to a CSV file
def save_to_csv(df, filename):
        df.to_csv(filename, index=False, header=True)

# Path to your CSV file
csv_file = 'dataset.csv'

# Check if the CSV file exists
if os.path.exists(csv_file):
    # Load the existing CSV into a DataFrame
    table = pd.read_csv(csv_file)
    print(f'CSV is found! Appending the existing one.')
    print(table)
else:
    # Create a new DataFrame and save it as a new CSV
    table = pd.DataFrame(columns=['id', 'photo', 'liked'])
    save_to_csv(table, csv_file)
    print(f'CSV-file was not found. Creating a new one.')


# Getting existing dialogs of a user, use to debug and get an ID of a dialog you need.
async def get_dialogs(client):
    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        print(dialog.title, dialog.id)

# User rates a person, it appends a CSV file.
async def rater(event, client):

    global table

    if event.message.media:

        current_id = 0 if len(table) == 0 else table['id'].max() + 1

        new_row = {'id':current_id, 'photo':'', 'liked':None}

        unique_filename = str(uuid.uuid4()) + '.jpg'
        download_path = 'base\ ' + unique_filename

        if hasattr(event.message.media, 'photo'):
            await client.download_media(event.message.media.photo, file=download_path)
            new_row['photo'] = unique_filename
            print('photo')
            print(new_row)
            table = pd.concat([table, pd.DataFrame([new_row])], ignore_index=True)
        elif hasattr(event.message.media, 'photos'):
            for i, photo in enumerate(event.message.media.photos):
                unique_filename = str(uuid.uuid4()) + '.jpg'
                new_row['photo'] = unique_filename
                print('photos')
                print(new_row)
                table = pd.concat([table, pd.DataFrame([new_row])], ignore_index=True)
                await client.download_media(photo, file=download_path)




async def main():
    # On how to get those, check telethon documentation
    api_id = ''
    api_hash = ''


    # Initializing a new session
    client = TelegramClient('first_sesh', api_id, api_hash, system_version="4.16.30-vxCUSTOM")
    await client.start()

    @client.on(events.NewMessage)
    async def handle_new_message(event):
        if event.message.sender_id == 1234060895:
            await rater(event, client)
            save_to_csv(table, csv_file)

    @client.on(events.NewMessage(outgoing=True))
    async def handle_my_message(event):
        if event.chat_id == 1234060895:
            message_content = event.message.text.strip()

            if '💌' in message_content or '❤️' in message_content:
                liked_status = 1
            elif '👎' in message_content:
                liked_status = 2
            elif message_content.isdigit() and int(message_content) in [1, 2]:
                liked_status = 1
            elif message_content.isdigit() and int(message_content) == 3:
                liked_status = 2
            else:
                return

            max_id = table['id'].max()
            print(max_id)
            print(table.loc[table['id'] == max_id, 'liked'].iloc[0])
            if pd.isna(table.loc[table['id'] == max_id, 'liked'].iloc[0]):
                print('done successfully')
                table.loc[table['id'] == max_id, 'liked'] = liked_status


    await client.run_until_disconnected()



asyncio.run(main())
