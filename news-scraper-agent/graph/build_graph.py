from typing import Callable

from langchain.schema.runnable import RunnableParallel
from langchain_community.llms import FakeListLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from agents.crawling_agent import CrawlingAgent
from agents.filtering_agent import FilteringAgent
from agents.html_parser_agent import HtmlParserAgent
from agents.message_agent import MessageAgent
from agents.sorting_agent import SortingAgent
from config.prompt_config import DefaultPromptTemplate
from graph.state import SiteState, State, PageCrawlingData
from models.site import SiteDto
from service.site_service import get_sites

MAX_NEWS_PER_CATEGORY = 3

AI_SITES = ["긱뉴스", "AI타임스", "데보션", "Google AI 뉴스"]
CLIMATE_SITES = ["Google 기후 환경 뉴스"]

SITE_NAME_MAPPING = {
    "네이버 뉴스 (정치)": "정치",
    "Google 정치 뉴스": "정치",
    "네이버 뉴스 (사회)": "사회",
    "Google 사회 뉴스": "사회",
    "네이버 뉴스 (생활/문화)": "생활/문화",
    "Google 생활 문화 뉴스": "생활/문화",
    "Google 기후 환경 뉴스": "기후",
    "네이버 스포츠": "스포츠",
    "Google 스포츠 뉴스": "스포츠",
    "네이버 연예": "연예",
    "Google 연예 뉴스": "연예",
    "AI타임스": "AI",
    "긱뉴스": "AI",
    "데보션": "AI",
    "Google AI 뉴스": "AI",
}

# FakeListLLM 설정
fake_responses = [
    "[]",
    "[]",
]
# llm = FakeListLLM(responses=fake_responses)  # FIXME 테스트 시 사용


def _get_prompts_for_category(category: str):
    """카테고리에 따라 적절한 필터링/소팅 프롬프트를 반환합니다."""
    # AI_SITES 리스트에 포함된 사이트들의 통합 카테고리는 "AI"입니다.
    # 기존 AI 전용 프롬프트를 사용하려면 None을 반환하도록 합니다.
    if category == "AI":
        return None, None
    elif category == "기후":
        return DefaultPromptTemplate.CLIMATE_FILTERING_PROMPT, DefaultPromptTemplate.CATEGORY_SORTING_PROMPT
    else:
        return DefaultPromptTemplate.CATEGORY_FILTERING_PROMPT, DefaultPromptTemplate.CATEGORY_SORTING_PROMPT


def parallel_crawl_filter(state: State) -> State:
    from config.log import NewsScraperAgentLogger
    logger = NewsScraperAgentLogger("GraphOrchestrator")
    sites = state.sites
    logger.info(f"🚀 Starting processing for {len(sites)} sites.")

    # --- 1단계: 사이트별 HTML 파싱 (고성능 병렬) ---
    logger.info("--- Phase 1: Parsing HTML (Parallel) ---")
    def parse_site(site: SiteDto):
        parser = HtmlParserAgent(site=site)
        initial_site_state = SiteState(
            crawling_result={}, filtering_result={}, parser_result={}, sorted_result={}
        )
        return parser(initial_site_state)

    parse_sequences = {
        f"parse_{site.name}": lambda x, site=site: parse_site(site)
        for site in sites
    }
    parse_runner = RunnableParallel(**parse_sequences)
    # 파싱은 LLM을 안 쓰므로 병렬로 수행 (max_concurrency: 5)
    parse_results: dict[str, SiteState] = parse_runner.invoke(state, config={"max_concurrency": 5})
    logger.info(f"✅ Finished Phase 1: All {len(sites)} sites parsed.")

    # --- 2단계: 사이트별 크로울링 (LLM 속도 제한 고려 순차) ---
    logger.info("--- Phase 2: LLM Crawling (Sequential for Rate-Limit) ---")
    crawled_results: list[SiteState] = []
    
    # gemini-2.0-flash는 RPM 15 정도이므로, sleep을 유지하며 하나씩 수행
    for site in sites:
        crawling_agent = CrawlingAgent(ChatGoogleGenerativeAI(model="gemini-2.0-flash"), site=site)
        # 1단계 결과 가져오기
        site_state = parse_results[f"parse_{site.name}"]
        logger.info(f"[{site.name}] Starting LLM crawl...")
        result_state = crawling_agent(site_state)
        crawled_results.append(result_state)
    logger.info("✅ Finished Phase 2: All sites crawled via LLM.")

    # --- 3단계: 카테고리별 데이터 병합 ---
    logger.info("--- Phase 3: Merging data by category ---")
    category_merged_raw_data: dict[str, list[PageCrawlingData]] = {}
    for i, site in enumerate(sites):
        site_result = crawled_results[i]
        category_name = SITE_NAME_MAPPING.get(site.name, site.name)
        if category_name not in category_merged_raw_data:
            category_merged_raw_data[category_name] = []
        category_merged_raw_data[category_name].extend(
            site_result.crawling_result.get(site.name, [])
        )
    logger.info(f"Categories identified: {list(category_merged_raw_data.keys())}")

    # --- 4단계: 카테고리별 최종 선별 (필터링 + 소팅) ---
    logger.info("--- Phase 4: Category Filtering & Sorting ---")
    from service.message_service import get_messages
    
    all_raw_articles = [art for arts in category_merged_raw_data.values() for art in arts]
    target_titles = [art.title for art in all_raw_articles if art.title]
    logger.info(f"Targeting {len(target_titles)} unique titles for duplicate check.")
    
    sent_messages = get_messages(target_titles)
    duplicate_titles = {
        msg.title for doc in sent_messages for msg in doc.messages if msg.title
    }
    logger.info(f"Found {len(duplicate_titles)} already sent titles.")

    session_added_titles = set()

    def process_category_selection(category: str, raw_articles: list[PageCrawlingData]):
        mock_site = SiteDto(name=category, url="", keywords=[], verified=True, requestedBy="system", createdAt=None, updatedAt=None)
        filtering_agent = FilteringAgent(ChatGoogleGenerativeAI(model="gemini-2.0-flash"), site=mock_site, prompt=_get_prompts_for_category(category)[0])
        sorting_agent = SortingAgent(ChatGoogleGenerativeAI(model="gemini-2.0-flash"), site=mock_site, prompt=_get_prompts_for_category(category)[1])

        # 1. 필터링
        logger.info(f"[{category}] Phase 4.1: LLM Filtering...")
        categorical_state = SiteState(crawling_result={category: raw_articles}, filtering_result={}, parser_result={}, sorted_result={})
        categorical_state = filtering_agent(categorical_state)
        candidates = categorical_state.filtering_result.get(category, [])
        
        # 2. 중복 제거
        fresh_candidates = [art for art in candidates if art.title not in duplicate_titles and art.title not in session_added_titles]
        if not fresh_candidates:
            logger.info(f"[{category}] No fresh articles after duplicate removal.")
            return []
            
        # 3. 소팅
        logger.info(f"[{category}] Phase 4.2: LLM Sorting for {len(fresh_candidates)} fresh articles...")
        categorical_state.filtering_result[category] = fresh_candidates
        categorical_state = sorting_agent(categorical_state)
        results = categorical_state.sorted_result.get(category, [])[:MAX_NEWS_PER_CATEGORY]
        
        for r in results:
            session_added_titles.add(r.title)
        return results

    final_sorted_results: dict[str, list[PageCrawlingData]] = {}
    for category, articles in category_merged_raw_data.items():
        if not articles: continue
        logger.info(f"[{category}] Selecting best articles out of {len(articles)}")
        final_sorted_results[category] = process_category_selection(category, articles)

    state.parallel_result = final_sorted_results
    logger.info(f"🏁 All processing finished. Total categories in result: {len(final_sorted_results)}")
    return state


def build_graph(initial_state: State):
    builder = StateGraph(State)

    # init node
    builder.add_node("start", lambda x: initial_state)
    builder.add_node("get_sites", get_sites)
    builder.add_node("parallel_crawl_filter", parallel_crawl_filter)
    builder.add_node("send_message", MessageAgent())

    # connect edge
    builder.add_edge(START, "start")
    builder.add_edge("start", "get_sites")
    builder.add_edge("get_sites", "parallel_crawl_filter")
    builder.add_edge("parallel_crawl_filter", "send_message")
    builder.add_edge("send_message", END)

    # graph run
    return builder.compile()
