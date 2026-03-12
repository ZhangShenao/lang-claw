"""
DeepResearch Sub-Agent 工具集

提供深度调研所需的搜索和分析工具。
"""

import logging
from typing import Any

from langchain_core.tools import tool
from tavily import TavilyClient

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def build_research_tools() -> list:
    """
    构建 DeepResearch Sub-Agent 的工具集。

    Returns:
        工具函数列表
    """

    @tool
    async def tavily_search(query: str, max_results: int = 5) -> dict[str, Any]:
        """
        使用 Tavily 进行深度网络搜索，适合复杂的研究查询。

        Args:
            query: 搜索查询字符串
            max_results: 返回的最大结果数（默认5个）

        Returns:
            包含搜索结果的字典，包括标题、URL、内容和原始回答
        """
        settings = get_settings()
        if not settings.tavily_api_key:
            logger.error("Tavily API key not configured")
            return {
                "error": "Tavily API key not configured. Please set TAVILY_API_KEY in environment.",
                "query": query,
                "results": [],
            }

        try:
            client = TavilyClient(api_key=settings.tavily_api_key)

            # 执行搜索
            response = client.search(
                query=query,
                max_results=max_results,
                include_answer=True,  # 包含 AI 生成的答案摘要
                search_depth="advanced",  # 使用高级搜索模式获得更深入的结果
            )

            # 格式化结果
            formatted_results = []
            for result in response.get("results", []):
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0),
                })

            return {
                "query": query,
                "answer": response.get("answer", ""),  # AI 生成的答案摘要
                "results": formatted_results,
                "total_results": len(formatted_results),
            }

        except Exception as e:
            logger.error(f"Tavily search failed: {e}", extra={"query": query})
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": [],
            }

    @tool
    def think_and_plan(thought: str) -> str:
        """
        记录思考过程和研究计划，帮助组织复杂的研究任务。

        这个工具不会执行实际操作，而是帮助你：
        - 明确研究目标
        - 分解研究步骤
        - 记录关键发现
        - 规划下一步行动

        Args:
            thought: 你的思考内容或研究计划

        Returns:
            确认信息
        """
        logger.info(f"Research thinking: {thought}")
        return f"✓ Thinking recorded: {thought}"

    @tool
    async def multi_query_search(
        queries: list[str],
        max_results_per_query: int = 3
    ) -> dict[str, Any]:
        """
        对多个查询进行并行搜索，适合需要对比或收集多方面信息的场景。

        Args:
            queries: 查询字符串列表（最多5个）
            max_results_per_query: 每个查询返回的最大结果数（默认3个）

        Returns:
            包含所有查询结果的字典
        """
        settings = get_settings()
        if not settings.tavily_api_key:
            logger.error("Tavily API key not configured")
            return {
                "error": "Tavily API key not configured.",
                "results": {},
            }

        # 限制查询数量
        queries = queries[:5]
        all_results: dict[str, Any] = {}

        try:
            client = TavilyClient(api_key=settings.tavily_api_key)

            for query in queries:
                try:
                    response = client.search(
                        query=query,
                        max_results=max_results_per_query,
                        include_answer=True,
                        search_depth="basic",  # 批量查询使用基础模式
                    )

                    all_results[query] = {
                        "answer": response.get("answer", ""),
                        "results": [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("url", ""),
                                "content": r.get("content", ""),
                            }
                            for r in response.get("results", [])
                        ],
                    }
                except Exception as e:
                    logger.warning(f"Query failed: {query}", extra={"error": str(e)})
                    all_results[query] = {"error": str(e), "results": []}

            return {
                "total_queries": len(queries),
                "successful_queries": sum(1 for r in all_results.values() if "error" not in r),
                "results": all_results,
            }

        except Exception as e:
            logger.error(f"Multi-query search failed: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": {},
            }

    return [
        tavily_search,
        think_and_plan,
        multi_query_search,
    ]
