from loader.connect import connect_db
from models.message import Message

def clear_all_messages():
    # DB 연결
    connect_db()
    
    # Message 컬렉션의 모든 데이터 삭제
    count = Message.objects.count()
    if count > 0:
        Message.objects.delete()
        print(f"✅ {count}개의 메시지 내역이 삭제되었습니다.")
    else:
        print("ℹ️ 삭제할 메시지 내역이 없습니다.")

if __name__ == "__main__":
    clear_all_messages()
