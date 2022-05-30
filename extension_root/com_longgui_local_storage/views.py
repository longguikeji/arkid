from pathlib import Path
from django.http import FileResponse
from arkid.core.api import api
@api.get("/tenant/{tenant_id}/localstorage/{file_name}", tags=["本地存储插件"], auth=None)
def get_file(request, tenant_id: str, file_name:str):
    """ 本地存储插件获取文件
    """    
    file_path = Path('./storage/') / file_name
    
    return FileResponse(
        open(file_path, 'rb')
    )