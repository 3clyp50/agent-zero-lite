from helpers.errors import handle_error
from helpers.tool import Tool, Response
from plugins._web_search.helpers import web_search


class SearchEngine(Tool):
    async def execute(self, query="", **kwargs):
        try:
            browser_model = self.agent.get_browser_model()
            if browser_model is None:
                raise RuntimeError("browser search model is unavailable")

            system_message, user_message = web_search.build_search_messages(
                query, web_search.SEARCH_ENGINE_RESULTS
            )
            response, reasoning = await browser_model.unified_call(
                system_message=system_message,
                user_message=user_message,
            )
            result = (response or reasoning or "").strip()
            if not result:
                raise RuntimeError("browser search model returned no content")
        except Exception as exc:
            handle_error(exc)
            result = f"Search Engine search failed: {exc}"

        await self.agent.handle_intervention(
            result
        )  # wait for intervention and handle it, if paused

        return Response(message=result, break_loop=False)
