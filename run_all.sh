#!/bin/bash

PROJECT_DIR="$(dirname "$0")"
SCRAPER_PORT=9000

echo "🚀 AI 뉴스 봇 시작"

# 1. scraper 서버 백그라운드 실행
echo "📡 Scraper 서버 시작 중..."
cd "$PROJECT_DIR/scraper-lambda"
~/.local/bin/poetry run python src/local_server.py &
SCRAPER_PID=$!

# 2. 서버 준비될 때까지 대기 (최대 15초)
for i in $(seq 1 15); do
    if curl -s -o /dev/null -X POST http://localhost:$SCRAPER_PORT 2>/dev/null; then
        break
    fi
    sleep 1
done
sleep 1
echo "✅ Scraper 서버 준비 완료"

# 3. 에이전트 실행
echo "🤖 뉴스 수집 시작..."
cd "../news-scraper-agent"
~/.local/bin/poetry run python3 main.py
AGENT_EXIT=$?

# 4. scraper 서버 종료
echo "🛑 Scraper 서버 종료 중..."
kill $SCRAPER_PID 2>/dev/null
wait $SCRAPER_PID 2>/dev/null

if [ $AGENT_EXIT -eq 0 ]; then
    echo "✅ 완료! 카카오워크를 확인하세요."
else
    echo "❌ 에러가 발생했습니다. (exit code: $AGENT_EXIT)"
fi
