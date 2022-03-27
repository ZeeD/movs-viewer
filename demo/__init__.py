from mypyui.settings import Settings
from mypyui.automation import get_movimenti
from movsmerger import merge_files

settings = Settings()
with get_movimenti(settings.username,
                   settings.password) as movimenti:
    print(movimenti)
    merge_files(settings.data_paths[0], movimenti)
