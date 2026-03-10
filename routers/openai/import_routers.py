"""Auto-generated router imports"""

from routers.openai.assistants import router as assistants_router
from routers.openai.audio import router as audio_router
from routers.openai.batches import router as batches_router
from routers.openai.chat import router as chat_router
from routers.openai.chatkit import router as chatkit_router
from routers.openai.completions import router as completions_router
from routers.openai.containers import router as containers_router
from routers.openai.conversations import router as conversations_router
from routers.openai.embeddings import router as embeddings_router
from routers.openai.evals import router as evals_router

# files router moved to common
# from routers.openai.files import router as files_router
from routers.openai.fine_tuning import router as fine_tuning_router
from routers.openai.images import router as images_router

# models router moved to common
# from routers.openai.models import router as models_router
from routers.openai.moderations import router as moderations_router
from routers.openai.organization import router as organization_router
from routers.openai.projects import router as projects_router
from routers.openai.projects import router as projects_router
from routers.openai.realtime import router as realtime_router
from routers.openai.responses import router as responses_router
from routers.openai.threads import router as threads_router
from routers.openai.uploads import router as uploads_router
from routers.openai.vector_stores import router as vector_stores_router
from routers.openai.videos import router as videos_router

ROUTERS = [
    assistants_router,
    audio_router,
    batches_router,
    chat_router,
    chatkit_router,
    completions_router,
    containers_router,
    conversations_router,
    embeddings_router,
    evals_router,
    fine_tuning_router,
    images_router,
    moderations_router,
    organization_router,
    projects_router,
    realtime_router,
    responses_router,
    threads_router,
    uploads_router,
    vector_stores_router,
    videos_router,
]
