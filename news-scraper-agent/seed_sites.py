from loader.connect import connect_db
from models.site import Site

connect_db()

sites = [
    {
        "name": "긱뉴스",
        "url": "https://news.hada.io",
        "keywords": ["AI", "LLM", "머신러닝", "딥러닝"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "AI타임스",
        "url": "https://www.aitimes.com",
        "keywords": ["AI", "인공지능", "LLM", "생성형AI"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "데보션",
        "url": "https://devocean.sk.com/blog/techBoardList.do?boardType=&searchData=&page=1&subIndex=&idList=",
        "keywords": ["AI", "LLM", "머신러닝"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "네이버 뉴스 (정치)",
        "url": "https://news.naver.com/section/100",
        "keywords": ["정치", "대선", "국회", "정당"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "네이버 뉴스 (사회)",
        "url": "https://news.naver.com/section/102",
        "keywords": ["사건", "사고", "사건사고", "재난"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "네이버 뉴스 (생활/문화)",
        "url": "https://news.naver.com/section/103",
        "keywords": ["생활", "문화", "건강", "교육"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "네이버 스포츠",
        "url": "https://sports.news.naver.com",
        "keywords": ["축구", "야구", "농구", "스포츠"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "네이버 연예",
        "url": "https://entertain.naver.com",
        "keywords": ["연예", "드라마", "영화", "K-pop"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google AI 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=AI+뉴스",
        "keywords": ["AI", "인공지능", "LLM", "정보기술"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 정치 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=정치+뉴스",
        "keywords": ["정치", "대선", "국회", "정당"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 사회 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=사회+뉴스",
        "keywords": ["사건", "사고", "재난"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 생활 문화 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=생활+문화+뉴스",
        "keywords": ["생활", "문화", "건강", "교육"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 기후 환경 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=기후+환경+뉴스",
        "keywords": ["기후", "환경", "날씨", "재난", "온난화"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 스포츠 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=스포츠+뉴스",
        "keywords": ["스포츠", "축구", "야구", "농구"],
        "verified": True,
        "requestedBy": "admin",
    },
    {
        "name": "Google 연예 뉴스",
        "url": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q=연예+뉴스",
        "keywords": ["연예", "드라마", "영화", "K-pop"],
        "verified": True,
        "requestedBy": "admin",
    },
]

for data in sites:
    if not Site.objects(name=data["name"]).first():
        site = Site(**data)
        site.save()
        print(f"✅ 등록 완료: {data['name']}")
    else:
        print(f"⏭️  이미 존재: {data['name']}")

print("\n등록된 사이트 목록:")
for site in Site.objects(verified=True):
    print(f"  - {site.name} ({site.url})")
