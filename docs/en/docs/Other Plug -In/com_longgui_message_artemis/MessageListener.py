from arkid.core.models import Message, User,TenantExtensionConfig
import stomp
from arkid.common.logger import logger
import json
from django.db.models.query_utils import Q

class MessageListener(stomp.ConnectionListener):

    def on_error(self, frame):
        logger.error(f"error : {frame}")

    def on_message(self, message):
        print(f"message {message}")
        data = json.loads(message.body)

        try:
            # 查找用户id
            users = data.get("users", None)
            if users and isinstance(users,list):
                users = User.active_objects.filter(Q(id__in=users)).all()
                data.pop("users")
            
            sender = User.active_objects.get(id=data.get("sender")) if data.get("sender",None) else None
            for user in users:
                message = Message(
                    title = data.get("title",""),
                    content = data.get("content",""),
                    user=user,
                    url =data.get("url",""),
                    sender=sender
                )
                message.save()
                
            
        except Exception as err:
            logger.error(err)