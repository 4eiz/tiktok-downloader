"""Module for handling user permissions and access control.
This module provides functionality to check if users are allowed to access
the bot based on their Telegram usernames and chat IDs configured in environment variables.
"""

import os
from typing import Optional
from telegram import Update

allowed_usernames = [x.strip() for x in os.getenv("ALLOWED_USERNAMES", "").split(",") if x]
allowed_chat_ids = [int(x.strip()) for x in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if x.strip()]
limit_bot_access = os.getenv("LIMIT_BOT_ACCESS", "True").lower() == "true"


def _read_ids(variable: str, default: str = "") -> set[int]:
    """Read a comma-separated list of Telegram IDs without failing on bad input."""
    ids = set()
    for value in os.getenv(variable, default).split(","):
        try:
            if value.strip():
                ids.add(int(value.strip()))
        except ValueError:
            continue
    return ids


# The project owner is always an administrator. ADMIN_IDS may add further admins.
admin_ids = _read_ids("ADMIN_IDS", "660502874")


# Check if user or chat is not allowed. Returns True if not allowed, False if allowed
def is_user_or_chat_not_allowed(
    username: Optional[str], chat_id: int, user_id: Optional[int] = None, dynamic_access: bool = False
) -> bool:
    """Check if username or chat_id is not in the allowed lists.

    Args:
        username: Telegram username to check
        chat: Telegram chat ID to check

    Returns:
        True if neither user nor chat is allowed, False if either is allowed
    """
    # default case when no limits are set
    if not limit_bot_access:
        return False

    # Administrators and IDs added from the in-bot allowlist always have access.
    if user_id in admin_ids or dynamic_access:
        return False

    # If chat_id is allowed, grant access regardless of username
    if chat_id in allowed_chat_ids:
        return False

    # Otherwise check if username is allowed
    return username not in allowed_usernames


def is_admin(user_id: Optional[int]) -> bool:
    """Return whether the Telegram user may manage the access list."""
    return user_id in admin_ids


# Function to inform the user they are not allowed to use the bot
async def inform_user_not_allowed(update: Update) -> None:
    """
    Informs the user that they are not allowed to use the bot.

    This function sends a message to the user indicating that they do not have permission
    to use the bot. It only responds if the chat type is private.

    Args:
        update (telegram.Update): Represents the incoming update from the Telegram bot.

    Returns:
        None
    """
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "🔒 <b>Доступ пока не открыт</b>\n\n"
            "Отправьте администратору эту команду — он добавит вас в белый список:\n"
            f"<code>/adduser {update.effective_user.id}</code>\n\n"
            f"Ваш ID: <code>{update.effective_user.id}</code>",
            parse_mode="HTML",
            reply_to_message_id=update.message.message_id,
        )


supported_sites = [
    "**https://",
    "facebook.com/",
    "instagram.com/",
    "tiktok.com/",
    "reddit.com/",
    "x.com/",
    "youtube.com/shorts",
]
