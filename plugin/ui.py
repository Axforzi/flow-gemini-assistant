# -*- coding: utf-8 -*-

import copy
from typing import List
import os, json

from flowlauncher import FlowLauncher, FlowLauncherAPI
from plugin.utils import api_request
from plugin.templates import *
from plugin.extensions import _l

from plugin.settings import settings_file, icon_path, ActionKeyword

AVAILABLE_MODELS = [
    {"name": "gemini-2.5-flash-lite", "desc": _l("Fast and lightweight (Recommended)"), "icon": "Images/gemini.png"},
    {"name": "gemini-2.5-flash", "desc": _l("Better balance between quality and speed"), "icon": "Images/gemini.png"},
    {"name": "gemini-3-pro-preview", "desc": _l("Smarter with better reasoning (Slow)"), "icon": "Images/gemini.png"}
]

class Main(FlowLauncher):
    messages_queue = []

    def sendNormalMess(self, title: str, subtitle: str):
        message = copy.deepcopy(RESULT_TEMPLATE)
        message["Title"] = title
        message["SubTitle"] = subtitle

        self.messages_queue.append(message)

    def sendActionMess(self, title: str, subtitle: str, method: str, value: List):
        # information
        message = copy.deepcopy(RESULT_TEMPLATE)
        message["Title"] = title
        message["SubTitle"] = subtitle

        # action
        action = copy.deepcopy(ACTION_TEMPLATE)
        action["JsonRPCAction"]["method"] = method
        action["JsonRPCAction"]["parameters"] = value
        message.update(action)

        self.messages_queue.append(message)

    def query(self, param: str) -> List[dict]:
        settings = self.load_settings()
        api_key = settings.get("api_key", "").strip()
        current_model = settings.get("model", "")

        q_lower = param.lower().strip()
        keyword = ActionKeyword

        # Nueva clave
        if q_lower.startswith("setkey"):
            new_key = param[6:].strip()  # Quitar "setkey"
            
            if not new_key:
                return [{
                    "Title": _l("Configure API Key"),
                    "SubTitle": _l("Paste your key here: {} setkey AIzaSy...").format(keyword),
                    "IcoPath": icon_path,
                    "JsonRPCAction": {"method": "fill_input", "parameters": ["setkey "], "dontHideAfterAction": True}
                }]
            
            return [{
                "Title": _l("Save Key: {}...").format(new_key[:15]),
                "SubTitle": _l("Press Enter to confirm and save."),
                "IcoPath": icon_path,
                "JsonRPCAction": {
                    "method": "save_config",
                    "parameters": ["api_key", new_key],
                    "dontHideAfterAction": True
                }
            }]
        
        # Nuevo modelo
        if q_lower.startswith("setmodel"):
            results = []
            for model in AVAILABLE_MODELS:
                is_current = _l(" (Current)") if model["name"] == current_model else ""
                results.append({
                    "Title": model["name"] + is_current,
                    "SubTitle": model["desc"],
                    "IcoPath": icon_path,
                    "JsonRPCAction": {
                        "method": "save_config",
                        "parameters": ["model", model["name"]],
                        "dontHideAfterAction": True
                    }
                })
            return results
        
        # VALIDACIÓN: SI FALTA LA KEY
        if not api_key:
            return [{
                "Title": _l("⚠️ Missing Google API Key"),
                "SubTitle": _l("Press Enter to write the configuration command"),
                "IcoPath": icon_path,
                "JsonRPCAction": {
                    "method": "change_query",
                    "parameters": [f"{keyword} setkey ", False], 
                    "dontHideAfterAction": True
                }
            }]
        
        # VALIDACIÓN: SI FALTA EL MODELO
        if not current_model:
            return [{
                "Title": _l("⚠️ Select a model"),
                "SubTitle": _l("Press Enter to see the list of models"),
                "IcoPath": icon_path,
                "JsonRPCAction": {
                    "method": "change_query",
                    "parameters": [f"{keyword} setmodel", True],
                    "dontHideAfterAction": True
                }
            }]
        
        if not q_lower or not q_lower.endswith("||"):
            return [{
                "Title": _l("Ask Gemini"),
                "SubTitle": _l("Write your query with || at the end to get the response..."),
                "IcoPath": icon_path
            }]
        
        return api_request(q_lower, current_model, api_key)
    
    def change_query(self, query, requery=False):
        FlowLauncherAPI.change_query(query, requery)
        
    def fill_input(self, text):
        keyword = ActionKeyword
        FlowLauncherAPI.change_query(f"{keyword} {text}", False)

    def load_settings(self):
        default = {"api_key": "", "model": ""}
        if not os.path.exists(settings_file):
            return default
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except:
            return default
        
    def save_config(self, key, value):
        settings = self.load_settings()
        settings[key] = value
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

        keyword = ActionKeyword
        FlowLauncherAPI.change_query(f"{keyword} ", False)
