from graph.build_graph import build_graph
from loader.connect import connect_db


def main() -> None:
    from config.log import NewsScraperAgentLogger
    logger = NewsScraperAgentLogger("Main")
    try:
        logger.info("🎬 Starting News Scraper Agent...")
        connect_db()
        from graph.state import State

        initial_state: State = State(
            sites=[],
            parallel_result={},
        )
        graph = build_graph(initial_state)
        graph.invoke(initial_state)
        logger.info("🏁 News Scraper Agent finished successfully.")
    except Exception as e:
        logger.critical(f"💥 News Scraper Agent failed with unhandled exception: {e}", exc_info=True)
        raise e


def lambda_handler(event, context) -> None:
    main()


if __name__ == "__main__":
    main()
