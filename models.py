import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert

base_dir = os.path.dirname(__file__) # 現在のファイルがあるディレクトリのパスを取得して、変数base_dirに代入
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')

db_engine=create_engine(database,echo=True)
Base=declarative_base()

db = SQLAlchemy()

class Shop(Base):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    cashless = Column(String(20), nullable=False)

    def __init__(self, name, address,lat,lng,cashless):
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.cashless = cashless


    def __repr__(self):
        return f"<Shop(name='{self.name}', address='{self.address}')>"
    
Base.metadata.create_all(db_engine)

session_maker= sessionmaker(bind=db_engine)
session=session_maker()

# session.query(Shop).delete() # session.queryクエリでItemモデルのデータを取得し、delete()メソッドで削除
# session.commit() # 上の操作をDBに書き込み・保存

# shops01=Shop("清六屋筑波大学店","茨城県つくば市天久保3丁目4-8",36.1059651,140.1004531,"非対応")

# session.add_all([shops01])
# session.commit()

item_all_list = session.query(Shop).order_by(Shop.id).all()
    # Itemモデルに基づく全データを、idの昇順で取得し、リストとして返す
for row in item_all_list:
    print(row)

# stmt=insert(Shop).values(
#     [{"name":"清六屋筑波大学店","address":"茨城県つくば市天久保3丁目4-8","lat":36.1059651,"lng":140.1004531,"cashless":"対応"}]
# )

# session.excute(stmt)
# session.commit()