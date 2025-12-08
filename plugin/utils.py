# -*- coding: utf-8 -*-


# Do your job at here.
# The script is better to write the core functions.
import requests
import tempfile
import os, json
from plugin.settings import icon_path
from plugin.extensions import _l

def api_request(query, model, api_key):
        try:
            clean_query = query.replace("||", "").strip()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = { 'Content-Type': 'application/json' }
            data = { "contents": [{"parts": [{"text": clean_query}]}] }
            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.text}")
            
            texto_respuesta = response.json()['candidates'][0]['content']['parts'][0]['text']
            return [
                {
                    "Title": texto_respuesta[:100] + "...",
                    "SubTitle": _l("Press Enter to copy all"),
                    "IcoPath": icon_path,
                    "JsonRPCAction": {
                        "method": "open_in_notepad",
                        "parameters": [texto_respuesta],
                        "dontHideAfterAction": False
                    }
                }
            ]
        except Exception as e:
            return [{
                "Title": _l("Error"),
                "SubTitle": str(e),
                "IcoPath": "Images/gemini.png"
            }]
        
def open_in_notepad(text):
        try:
            fd, path = tempfile.mkstemp(suffix=".txt", text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(text)
            os.startfile(path)
            
        except Exception as e:
            os.system(f'echo Error al abrir bloc de notas: {str(e)} | clip')


def get_keyword():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = folder_path.split('\\')[:-1]
    plugin_settings = '\\'.join(folder_path) + "\\plugin.json"

    folder_path = folder_path[:-2]
    plugins_settings_flowlauncher = '\\'.join(folder_path) + "\\Settings\\settings.json"

    # CONFIG Plugin
    with open(plugin_settings, 'r') as f:
        settings = json.load(f)
        plugin_id = settings["ID"]

    # CONFIG FlowLauncher
    with open(plugins_settings_flowlauncher, 'r') as f:
        settings = json.load(f)
        settings = settings["PluginSettings"]["Plugins"]
        find_plugin = {key: value for key, value in settings.items() if key == plugin_id}
        ActionKeywords = find_plugin[plugin_id]["ActionKeywords"][0]

    return ActionKeywords
