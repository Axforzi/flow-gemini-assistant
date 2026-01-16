# -*- coding: utf-8 -*-


# Do your job at here.
# The script is better to write the core functions.
import requests
import tempfile
import os, subprocess
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
                    "Title": _l("Open in Notepad"),
                    "SubTitle": _l("See the full response in Notepad"),
                    "IcoPath": icon_path,
                    "JsonRPCAction": {
                        "method": "open_in_notepad",
                        "parameters": [texto_respuesta, clean_query],
                        "dontHideAfterAction": False
                    }
                },
                {
                    "Title": _l("Copy to Clipboard"),
                    "SubTitle": texto_respuesta[:100].replace("\n", " ") + "...",
                    "IcoPath": icon_path,
                    "JsonRPCAction": {
                        "method": "copy_to_clipboard",
                        "parameters": [texto_respuesta],
                        "dontHideAfterAction": False
                    }
                }
            ]
        except Exception as e:
            return [{
                "Title": _l("Error"),
                "SubTitle": str(e),
                "IcoPath": icon_path
            }]
        
def open_in_notepad(text, query):
        try:
            fd, path = tempfile.mkstemp(prefix=query[:20].replace(' ', '_') + "_", suffix=".txt", text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(text)
            os.startfile(path)
            
        except Exception as e:
            subprocess.run(['clip.exe'], input=f'Error al abrir bloc de notas: {str(e)}'.encode('utf-8'))

def copy_to_clipboard(text):
    subprocess.run(['clip.exe'], input=text.strip().encode('utf-8'))