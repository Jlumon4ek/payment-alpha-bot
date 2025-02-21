from presentation.handlers.admin import router as admin_router
from presentation.handlers.users import router as user_router
from presentation.handlers.subscription import router as subscription_router


router_list = [
    admin_router,
    subscription_router,
    user_router,
]