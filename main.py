import asyncio
import json
import requests

from functions import get_updates, promote_user, set_custom_title
from config import tg_api_link, exc_ids
from secretData import bot_token, chat_id


async def set_status():
    while True:
        active_ids = await get_updates()

        if active_ids is not None and active_ids != []:
            admin_ids = list()

            try:
                admins = json.loads(requests.get(f'{tg_api_link}{bot_token}/getChatAdministrators',
                                                 params={'chat_id': chat_id}
                                                 ).text)['result']

                for admin in admins:
                    user_id = admin['user']['id']
                    admin_ids.append(user_id)

                for i in active_ids:
                    if i in exc_ids:
                        continue

                    if i not in admin_ids:
                        for j in admin_ids[::-1]:

                            if j in exc_ids:
                                continue

                            if j not in active_ids:
                                result = await promote_user(j, False)

                                if result['ok']:
                                    admin_ids.remove(j)
                                    await asyncio.sleep(1)

                                else:
                                    err_code = result['error_code']
                                    err = result['description']
                                    print(f'Error in de-promote ({j}) user. Error code: {err_code}. Error: {err}.')

                        result = await promote_user(i, True)

                        if result['ok']:
                            admin_ids.append(i)
                            await set_custom_title(i)

                    else:
                        await set_custom_title(i)

            except Exception as e:
                print(f'Error in Set status. Check the logs:\n{e}')

        await asyncio.sleep(180)


if __name__ == '__main__':
    asyncio.create_task(set_status())
