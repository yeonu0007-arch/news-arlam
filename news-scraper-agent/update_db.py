from loader.connect import connect_db
from models.site import Site

connect_db()

naver_climate = Site.objects(name="네이버 뉴스 (기후/환경)").first()
if naver_climate:
    naver_climate.delete()
    print("Deleted '네이버 뉴스 (기후/환경)' from DB.")
else:
    print("'네이버 뉴스 (기후/환경)' not found in DB.")
