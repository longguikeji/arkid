from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
import stomp
from common.logger import logger
import json

class MessageListener(stomp.ConnectionListener):
    
    def on_error(self, frame):
        print(f"error : {frame}")
        
        
    def on_message(self, message):
        from ..models import Message
        from app.models import App
        from django.contrib.auth import get_user_model

        User = get_user_model()
        
        print(f"message {message}")
        data = json.loads(message.body)
        
        try:
            app = App.active_objects.get(uuid=data.pop("app_id"))
            
            users = data.pop("users")
            print(data)
            
            if users:
                users = User.active_objects.filter(Q(uuid__in=users)).all()
            
            message = Message(
                app=app,
                **data
            )
            if users:
                message.users.set(users)
            message.save()
            
        except Exception as err:
            logger.error(err)