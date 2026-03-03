from zoneinfo import ZoneInfo

from datetime import datetime

from graph.state import CrawlingResult
from external.kakaowork.message_blocks import (
    KakaoworkMessageRequest,
    HeaderBlock,
    DividerBlock,
    ButtonBlock,
    ButtonActionBlock,
    TextBlock,
    InnerTextBlock,
    SectionBlock,
    InnerTextUrlBlock,
)


class KakaoworkMessageBuilder:
    def __init__(self):
        # none
        pass

    @staticmethod
    def build(unique_site_news_dict: CrawlingResult) -> KakaoworkMessageRequest:
        has_empty_list = all(
            len(page_crawling_data_list) == 0
            for site_name, page_crawling_data_list in unique_site_news_dict.items()
        )

        today = datetime.now(tz=ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

        blocks = [HeaderBlock(text=f"📢 {today} 오늘의 뉴스", style="blue")]
        if has_empty_list:
            blocks.append(
                TextBlock(
                    inlines=[
                        InnerTextBlock(text="오늘은 소식이 없어요! 😅", bold=False)
                    ]
                )
            )
        else:
            for site_name, site_data in unique_site_news_dict.items():
                if len(site_data) == 0:
                    continue

                blocks.append(
                    TextBlock(
                        text=site_name,
                        inlines=[InnerTextBlock(text=site_name, bold=True)],
                    )
                )
                inlines = []
                for idx, item in enumerate(site_data):
                    if item.title and item.url:
                        is_last_item = idx == len(site_data) - 1
                        # 가독성을 위해 각 뉴스별 마지막 기사는 구분선(\n) 한 개 더 추가
                        title = (
                            f"{item.title}\n" if is_last_item else f"{item.title}\n\n"
                        )
                        inlines.append(InnerTextUrlBlock(text=title, url=item.url))
                blocks.append(SectionBlock(content=TextBlock(inlines=inlines)))
                blocks.append(DividerBlock())

        blocks.append(
            ButtonBlock(
                text="사이트 추가하기",
                action=ButtonActionBlock(
                    value="https://d1qbk7p5aewspc.cloudfront.net/index.html"
                ),
            )
        )

        return KakaoworkMessageRequest(text=f"📢 {today} 오늘의 뉴스", blocks=blocks)
