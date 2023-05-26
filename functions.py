import asyncio
import json
import requests
import psycopg2

from pytonlib.utils import address

from config import tg_api_link, tonapi_link, database_url, collection, nft_name, allowed_updates
from secretData import bot_token, tonapi_token, chat_id


async def open_connection():
    connect = psycopg2.connect(database_url)
    cursor = connect.cursor()
    return connect, cursor


async def close_connection(connect):
    connect.commit()
    connect.close()


async def get_user_nfts(user_address):
    try:
        readable_address = address.detect_address(user_address)['bounceable']['b64url']
        nfts = json.loads(requests.get(f'{tonapi_link}nft/searchItems',
                                       params={'owner': readable_address,
                                               'collection': collection,
                                               'include_on_sale': True,
                                               'limit': 5000,
                                               'offset': 0},
                                       headers={'Authorization': 'Bearer ' + tonapi_token}
                                       ).text)['nft_items']
        return len(nfts)

    except Exception as e:
        print(f'Error in Get User Nft method with ({user_address}) address. Check the logs:\n{e}.')
        return False


async def get_updates():
    ids = list()
    try:
        updates = json.loads(requests.get(f'{tg_api_link}{bot_token}/getUpdates',
                                          params={'offset': 100,
                                                  'allowed_updates': allowed_updates}
                                          ).text)['result']

        for update in updates:
            if 'message' in update:
                message = update['message']
            elif 'edited_message' in update:
                message = update['edited_message']

            if message['chat']['id'] == chat_id and not message['from']['is_bot']:
                user_id = message['from']['id']
                if len(ids) > 50:
                    break
                if user_id not in ids:
                    ids.append(user_id)

    except Exception as e:
        print(f'Error in Get Updates method. Check the logs:\n{e}')

    return ids


async def promote_user(user_id, chat_manage_flag):
    return json.loads(requests.get(f'{tg_api_link}{bot_token}/promoteChatMember',
                                   params={'chat_id': chat_id,
                                           'user_id': user_id,
                                           'can_post_messages': True,
                                           'can_edit_messages': True,
                                           'can_manage_chat': chat_manage_flag}
                                   ).text)


async def set_custom_title(tg_id):
    connect, cursor = await open_connection()
    cursor.execute(f'select owner from numbers_verify where tgid = {tg_id}')
    row = cursor.fetchone()
    if row is None:
        await promote_user(tg_id, False)
        await close_connection(connect)
        return
    (user_address,) = row
    await close_connection(connect)

    if user_address is not None:
        nfts_count = await get_user_nfts(user_address)

        if nfts_count > 0:
            if nfts_count == 1:
                text = nft_name
            else:
                text = f'{nft_name}s'

            result = json.loads(requests.get(f'{tg_api_link}{bot_token}/setChatAdministratorCustomTitle',
                                             params={'chat_id': chat_id,
                                                     'user_id': tg_id,
                                                     'custom_title': f'{nfts_count} {text}'}
                                             ).text)
            await asyncio.sleep(3)

            if not result['ok']:
                err_code = result['error_code']
                err = result['description']
                print(f'Error in Set Custom Title to ({tg_id}) user. Error code: {err_code}. Error: {err}.')
