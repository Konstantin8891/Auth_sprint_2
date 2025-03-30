"""Пользовательские ручки кролика."""

import logging
import uuid
from typing import Dict, Union

from fastapi import Depends

from broker.rabbitmq import exch
from broker.rabbitmq import rabbit_router as rabbit_users_router
from exceptions.users import UserNotFound
from models.entity import User
from schemas.entity import UserRoleSchema
from services.users import UserService, get_user_service

logger = logging.getLogger(__name__)


@rabbit_users_router.subscriber("me", exch, response_model=UserRoleSchema)
async def get_me(message: uuid.UUID, user_service: UserService = Depends(get_user_service)) -> Union[Dict, User]:
    """Получение пользователя из токена и не только."""
    try:
        return await user_service.get_user_by_id(user_id=message)
    except UserNotFound as e:
        logger.error(e)
        return {"status_code": 404, "detail": str(e)}
    except Exception as e:
        logger.error(e)
        return {"status_code": 400, "detail": str(e)}
