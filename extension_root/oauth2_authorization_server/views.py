from app.models import App
from oauth2_provider.models import get_application_model
from oauth2_provider.views import AuthorizationView as BaseAuthorizationView
from urllib.parse import urlparse
import re

class AuthorizationView(BaseAuthorizationView):
    
    def create_authorization_response(self, request, scopes, credentials, allow):
        
        uri, headers, body, status = super().create_authorization_response(
            request, scopes, credentials, allow
        )
        
        try:
            from extension_root.application_multiple_ip.models import ApplicationMultipleIp
            application = get_application_model().objects.get(client_id=credentials["client_id"])
            app = App.active_objects.get(id=application.name)
            ipregxs = ApplicationMultipleIp.active_objects.filter(app=app).all()
            request_host = self.context["request"].get_host()
           
            for ipregx in ipregxs:
                if re.match(ipregx.ip_regx,request_host):
                    o = urlparse(uri)
                    uri = re.sub(o.hostname,ipregx.ip,uri)
                    continue
                    
        except Exception as err:
            print(err)
            
        return uri, headers, body, status