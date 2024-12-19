from bot.users.router import router as users_router
from bot.subscription.router import router as subscription_router
from bot.admin.router import router as admin_router

router_list = [
    users_router,
    subscription_router,
    admin_router,
]