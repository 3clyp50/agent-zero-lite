from helpers.extension import Extension
from plugins._web_search.helpers import web_search


class MissingApiKeyCheck(Extension):
    CONFIGURE_MODEL_SETTINGS_LINK = (
        """<div class="onboarding-banner-btn-container" style="margin-top: 12px;">"""
        """<button class="btn btn-ok" onclick="window.openModal('/plugins/_model_config/webui/config.html');return false;">"""
        """Open Model Settings</button>"""
        """</div>"""
    )

    async def execute(self, banners: list = [], frontend_context: dict = {}, **kwargs):
        browser_cfg = web_search.get_browser_model_config()
        provider = (browser_cfg.get("provider", "") or "").strip()

        if not provider:
            return

        if web_search.has_provider_api_key(provider, browser_cfg.get("api_key", "")):
            return

        banners.append({
            "id": "missing-web-search-api-key",
            "type": "warning",
            "priority": 90,
            "title": "Live web search is not ready",
            "html": f"""The builtin web search model is configured for <code>{provider}/{browser_cfg.get("name", "")}</code>, but no API key was found.<br>
                     Add the required provider key to enable live search results.
                     {self.CONFIGURE_MODEL_SETTINGS_LINK}""",
            "dismissible": True,
            "source": "backend",
        })
