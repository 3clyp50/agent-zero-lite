from helpers.extension import Extension
from plugins._web_search.helpers.web_search import build_browser_model


class BrowserModelProvider(Extension):
    def execute(self, data: dict = {}, **kwargs):
        if self.agent:
            data["result"] = build_browser_model(self.agent)
