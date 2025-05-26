from app import app, db
from models import Shop

with app.app_context():
    shops = Shop.query.all()

    if shops:
        print("現在のテーブルの内容:")
        for shop in shops:
            print(f"ID: {shop.id}, Name: {shop.name}, Address: {shop.address},Lat:{shop.lat},Lng:{shop.lng},Cashless:{shop.cashless}")
            # 必要に応じて他の属性も表示
    else:
        print("テーブルにはデータがありません。")