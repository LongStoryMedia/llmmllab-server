"""Auto-generated router imports"""

from routers.anthropic.messages import router as messages_router

# models and files routers moved to common
# from routers.anthropic.models import router as models_router
# from routers.anthropic.files import router as files_router
from routers.anthropic.completions import router as completions_router

ROUTERS = [
    messages_router,
    completions_router,
]
