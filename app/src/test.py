import asyncio
import json
import os
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins
from aiogram import Bot
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from domain.models.subscription import Subscription

# ======================== НАСТРОЙКИ ========================
API_ID = "4580714"
API_HASH = "85e95a427d7ce02be021036f84ba8706"
BOT_TOKEN = "7556338114:AAGd7XuXLFGH_NPmhY87UmRPiAQwJ3vwj9E"
DATABASE_URL = "postgresql://Ey5De9S2B4zZXt7d:f3ASvKqGxVErNQaM@localhost:5432/pwWB8Y7VKp4aGtUe5"

CHANNEL_ID = -1002450256034
DISCUSSION_GROUP_ID = -1002317479882

MEMBERS_JSON = "members.json"
TOTAL_MEMBERS_TARGET = 527
# ===========================================================


async def get_active_subscriptions(engine):
    """
    Получаем telegram_id пользователей с активной подпиской из БД.
    Возвращаем set со списком ID.
    """
    try:
        stmt = select(Subscription.telegram_id).where(Subscription.isActive == True)
        with Session(engine) as session:
            result = session.execute(stmt).scalars().all()
        return set(result)
    except Exception as e:
        print(f"[ERROR] Ошибка при получении подписок: {e}")
        return set()


def load_members() -> dict:
    """Загружаем словарь участников из JSON"""
    if not os.path.exists(MEMBERS_JSON):
        return {}
    
    with open(MEMBERS_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    return data


def save_members(data: dict):
    """Сохраняем словарь участников в JSON"""
    with open(MEMBERS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def get_all_admins(client: TelegramClient):
    """Получаем список админов через Telethon"""
    try:
        admins = []
        async for participant in client.iter_participants(CHANNEL_ID, filter=ChannelParticipantsAdmins):
            admins.append(participant.id)
        print(f"[INFO] Найдено {len(admins)} администраторов в канале")
        return set(admins)
    except Exception as e:
        print(f"[ERROR] Ошибка при получении админов: {e}")
        return set()


async def fetch_members_iter(client: TelegramClient, known_members: dict):
    """
    Получаем всех участников канала через пользовательский аккаунт
    """
    count_before = len(known_members)
    new_members_count = 0
    print("[DEBUG] Начинаем получение участников...")

    try:
        # Получаем всех участников
        async for participant in client.iter_participants(CHANNEL_ID):
            if participant.bot:
                continue

            tid_str = str(participant.id)
            
            # Добавляем нового участника
            if tid_str not in known_members:
                known_members[tid_str] = {"isChecked": False}
                new_members_count += 1
                
                if new_members_count % 50 == 0:
                    print(f"[INFO] Получено {new_members_count} новых участников...")

            # Проверяем достижение цели
            if len(known_members) >= TOTAL_MEMBERS_TARGET:
                print(f"[INFO] Достигнуто {TOTAL_MEMBERS_TARGET} участников")
                break

    except Exception as e:
        print(f"[ERROR] Ошибка при получении участников: {e}")

    count_after = len(known_members)
    print(f"[INFO] Добавлено {count_after - count_before} новых участников")
    return known_members


async def main():
    # Инициализация клиентов
    client = TelegramClient('cleanup_session', API_ID, API_HASH)
    bot = Bot(token=BOT_TOKEN)
    engine = create_engine(DATABASE_URL)

    try:
        print("[START] Начинаем очистку...")

        # Стартуем Telethon-клиент
        await client.start()
        
        # Загружаем список активных подписок
        active_subs = await get_active_subscriptions(engine)
        print(f"[INFO] Найдено {len(active_subs)} активных подписок")

        # Загружаем текущий JSON
        members_data = load_members()

        # Получаем админов через Telethon
        admin_ids = await get_all_admins(client)

        # Получаем участников канала
        print("[INFO] Получаем список участников канала...")
        members_data = await fetch_members_iter(client, members_data)
        
        # Сохраняем промежуточный результат
        save_members(members_data)
        print(f"[INFO] Всего в JSON: {len(members_data)} участников")

        # Счётчики
        kicked_count = 0
        error_count = 0

        # Обходим всех пользователей
        for tid_str, info in members_data.items():
            if info["isChecked"]:
                continue

            user_id = int(tid_str)

            # Проверяем подписку и админку
            if user_id not in active_subs and user_id not in admin_ids:
                try:
                    # Баним в канале
                    try:
                        await bot.ban_chat_member(CHANNEL_ID, user_id)
                        print(f"[+] Пользователь {user_id} удалён из канала")
                        kicked_count += 1
                    except Exception as e:
                        print(f"[-] Ошибка при удалении из канала {user_id}: {e}")
                        error_count += 1

                    # Баним в группе
                    try:
                        await bot.ban_chat_member(DISCUSSION_GROUP_ID, user_id)
                        print(f"[+] Пользователь {user_id} удалён из группы обсуждения")
                    except Exception as e:
                        print(f"[-] Ошибка при удалении из группы {user_id}: {e}")

                except Exception as e:
                    print(f"[ERROR] Общая ошибка при обработке {user_id}: {e}")
                    error_count += 1

            # Отмечаем как проверенного
            info["isChecked"] = True

        # Сохраняем финальные изменения
        save_members(members_data)

        print(f"\n[ИТОГИ]")
        print(f"Всего уникальных пользователей в JSON: {len(members_data)}")
        print(f"Удалено пользователей: {kicked_count}")
        print(f"Ошибок: {error_count}")

    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
    finally:
        # Завершаем сессии
        await client.disconnect()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
