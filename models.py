import os
from sqlalchemy import create_engine, Column, Integer, String, Float, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 現在のファイルがあるディレクトリのパスを取得
base_dir = os.path.dirname(__file__)
# データベースファイルのパスを設定
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')

# データベースエンジンを作成（echo=TrueでSQLログを表示）
db_engine = create_engine(database, echo=True)
# 宣言的ベースを作成（モデルの基底クラス）
Base = declarative_base()

# Shopモデルの定義
class Shop(Base):
    __tablename__ = 'shops' # テーブル名を指定
    id = Column(Integer, primary_key=True) # IDカラム（主キー）
    name = Column(String(255), nullable=False) # 店舗名
    address = Column(String(255), nullable=False) # 住所
    lat = Column(Float, nullable=False) # 緯度
    lng = Column(Float, nullable=False) # 経度
    cashless = Column(String(20), nullable=False) # キャッシュレス対応状況
    opening_hours = Column(String(255), nullable=True) # 営業時間
    regular_holidays = Column(String(255), nullable=True) # 定休日

    # コンストラクタ（Shopオブジェクト作成時に呼ばれる）
    def __init__(self, name, address, lat, lng, cashless, opening_hours=None, regular_holidays=None):
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.cashless = cashless
        self.opening_hours = opening_hours
        self.regular_holidays = regular_holidays

    # オブジェクトをprintしたときに表示される文字列（デバッグ用）
    def __repr__(self):
        return (f"<Shop(id={self.id}, name='{self.name}', address='{self.address}', "
                f"cashless='{self.cashless}', opening_hours='{self.opening_hours}', "
                f"regular_holidays='{self.regular_holidays}')>")

# データベースにテーブルを作成（既に存在する場合はスキップ）
Base.metadata.create_all(db_engine)

# セッションメーカーを作成し、セッションを取得
session_maker = sessionmaker(bind=db_engine)
session = session_maker()

# --- データベースにデータを投入する方法 ---

# ここは、以前のデータ投入スクリプトのコメントアウト部分です。
# データベースにデータが存在するかどうかのチェックは、session.query(Shop).count() を使います。
# データベースに初期データがあるかを確認し、なければ追加するロジック
if session.query(Shop).count() == 0:
    # 新しいShopオブジェクトを作成し、営業時間と定休日を追加
    shops_to_insert = [
        Shop("清六屋筑波大学店", "茨城県つくば市天久保3丁目4-8", 36.1059651, 140.1004531, "非対応", "00:00-24:00", "無し"),
        Shop("ららららーめんや", "茨城県つくば市天久保1-6-11", 36.09133965552778, 140.110440725301, "非対応", "11:00-22:00", "月曜日"),
        Shop("七福軒", "茨城県つくば市天久保1-6-14", 36.09095296386704, 140.10967577302563, "非対応", "11:30-14:30, 17:30-21:00", "火曜日"),
        Shop("らーめん ICHI", "茨城県つくば市天久保1-6-15", 36.09060120154453, 140.10896079222297, "非対応", "11:00-15:00", "日曜日")
    ]
    session.add_all(shops_to_insert)
    session.commit()
    print("初期データを投入しました。")
else:
    print("データベースには既にデータが存在します。")

# --- 既存のショップデータに営業時間と定休日を追加するデータ ---
# ここに、あなたが更新したいショップの名前と、対応する営業時間・定休日の情報を入力してください。
# ユーザーが提供したショップリストに、仮の営業時間と定休日を追加しました。
# 実際のデータに置き換えてください。
# ★修正点: shop_updates_data のキーをデータベースの店舗名と完全に一致させました。
shop_updates_data = {
    "清六屋筑波大学店": {"regular_holidays": "なし", "opening_hours": "24時間営業"},
    "ららららーめんや": {"regular_holidays": "日曜定休", "opening_hours": "18:00-5:00"},
    "つけめん・まぜそばむじゃき": {"regular_holidays": "なし", "opening_hours": "11:30-14:30, 17:30-22:00"},
    "七福軒": {"regular_holidays": "なし", "opening_hours": "平日: 11:00-14:00, 18:00-22:00; 日: 11:00-14:30, 17:30-21:00"},
    "らーめん ICHI": {"regular_holidays": "なし", "opening_hours": "月火: 19:00-1:00; 水木: 10:00-13:30, 19:00-1:00; 金土: 10:00-13:30, 19:00-2:00; 日: 10:00-13:30"},
    "大元": {"regular_holidays": "日曜定休", "opening_hours": "22:00-3:00"},
    "麺屋とみよし": {"regular_holidays": "火曜定休", "opening_hours": "11:30-14:30"},
    "ラーメン刻": {"regular_holidays": "なし", "opening_hours": "11:00-24:00"},
    "特級中華蕎麦 洋介 2号店": {"regular_holidays": "月曜定休", "opening_hours": "平日: 11:30-14:30, 17:30-23:00; 土: 11:30-15:00, 17:30-24:00; 日: 11:30-15:00, 17:30-23:00"},
    "芛堂寺": {"regular_holidays": "なし", "opening_hours": "11:30-14:30, 18:00-21:30"},
    "活龍大衆麺処 真壁屋": {"regular_holidays": "なし", "opening_hours": "17:30-14:00, 17:30-21:30"},
    "煮干中華ソバ イチカワ": {"regular_holidays": "日曜日", "opening_hours": "11:30-材料がなくなり次第終了"},
    "担担麺ロシュー": {"regular_holidays": "月曜日", "opening_hours": "11:00-14:30"},
    "鶏々": {"regular_holidays": "なし", "opening_hours": "11:30-14:30, 18:00-23:00"},
    "ごう家": {"regular_holidays": "なし", "opening_hours": "平日: 11:30-14:30, 17:30-00:00; 日曜: 00:00-22:00"},
    "ラーメン異国龍": {"regular_holidays": "月曜日", "opening_hours": "11:30-14:30, 17:30-22:00"},
    "麵屋秀彬": {"regular_holidays": "月曜日", "opening_hours": "火-日: 11:00-14:30, 20:00-1:00"},
    "俺の生きる道W": {"regular_holidays": "なし", "opening_hours": "11:00-14:00, 18:00-00:00"},
    "麵や小五郎": {"regular_holidays": "月曜定休", "opening_hours": "火-木: 11:30-14:00, 17:30-22:30; 金土: 11:30-14:00, 17:30-23:30; 日: 11:30-14:00, 17:00-21:00"}, 
    "特級鶏蕎麦龍介テクノパーク桜店": {"regular_holidays": "なし", "opening_hours": "11:30-14:30, 17:30-21:30"}, 
    "博多拉麺一休": {"regular_holidays": "なし", "opening_hours": "平日: 11:30-22:30; 火: 17:00-22:30"},
    "中華そば騰匠俐": {"regular_holidays": "なし", "opening_hours": "11:00-15:00, 17:00-21:00"}, 
    "珍来テクノパーク桜店": {"regular_holidays": "水木定休", "opening_hours": "11:30-21:00"}, 
    "珍來つくば松代店": {"regular_holidays": "なし", "opening_hours": "11:00-1:00"},    
    "銀の豚": {"regular_holidays": "火曜日", "opening_hours": "11:00-22:00"},
    "はりけんラーメン": {"regular_holidays": "月曜定休", "opening_hours": "11:30-14:30, 17:30-21:00"}
}

print("--- 既存のショップデータを更新中 ---")
for shop_name, update_info in shop_updates_data.items():
    # 名前でショップを検索します。
    shop = session.query(Shop).filter_by(name=shop_name).first()

    if shop:
        # 営業時間と定休日を更新します。
        shop.opening_hours = update_info["opening_hours"]
        shop.regular_holidays = update_info["regular_holidays"]
        print(f"'{shop_name}' の営業時間と定休日を更新しました。")
    else:
        print(f"'{shop_name}' はデータベースに見つかりませんでした。")

# 変更をデータベースにコミット（保存）します。
session.commit()
print("--- ショップデータの更新が完了しました ---")

# --- データベースから全データを取得して表示 ---
item_all_list = session.query(Shop).order_by(Shop.id).all()
# Itemモデルに基づく全データを、idの昇順で取得し、リストとして返す
print("\n--- 更新後のデータベースに保存されている全データ ---")
for row in item_all_list:
    print(row)

# セッションを閉じる（重要）。
session.close()
