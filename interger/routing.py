from django.urls import path
from .consumers import WSConsumer
ws_urlpatterns = [
    path("ws/some_url/", WSConsumer.as_asgi()),
]
# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })