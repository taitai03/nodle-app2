import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
import re # 正規表現モジュールをインポート

base_dir = os.path.dirname(__file__)
database_file = 'data.sqlite'
database = 'sqlite:///' + os.path.join(base_dir, database_file)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    cashless = db.Column(db.String(20), nullable=False)
    opening_hours = db.Column(db.String(255), nullable=True) # 営業時間カラム
    regular_holidays = db.Column(db.String(255), nullable=True) # 定休日カラム

    def __init__(self, name, address, lat, lng, cashless, opening_hours=None, regular_holidays=None):
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.cashless = cashless
        self.opening_hours = opening_hours
        self.regular_holidays = regular_holidays

    def __repr__(self):
        return (f"<Shop(id={self.id}, name='{self.name}', address='{self.address}', "
                f"cashless='{self.cashless}', opening_hours='{self.opening_hours}', "
                f"regular_holidays='{self.regular_holidays}')>")


def is_shop_currently_open(opening_hours_str, regular_holidays_str, current_datetime):
    # 定休日チェック
    if regular_holidays_str:
        today_weekday_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"][current_datetime.weekday()]
        
        # 定休日文字列に今日の曜日が含まれていたら定休日
        if today_weekday_jp in regular_holidays_str:
            return False, "定休日"
        
        # "なし" や "無し" は定休日ではないのでスキップ
        if "なし" in regular_holidays_str or "無し" in regular_holidays_str:
            pass 
        
        # "不定休" の場合は、営業時間で判断を試みるが、厳密には「要確認」が良い
        if "不定休" in regular_holidays_str:
            pass # 営業時間で判断を続ける

    # 営業時間情報がない場合は閉じていると判断
    if not opening_hours_str:
        return False, "営業時間情報なし" 

    # 24時間営業のケース
    if "24時間営業" in opening_hours_str:
        return True, "営業中 (24時間)"
    
    # 特殊な記述のケース（例: 材料がなくなり次第終了）
    if "材料がなくなり次第終了" in opening_hours_str:
        return False, "営業中 (要確認)" # プログラムで判断できないため、要確認とする

    current_time = current_datetime.time()
    current_weekday = current_datetime.weekday() # 0=月, 6=日
    
    target_hours_str = None
    segments = opening_hours_str.split(';')

    for segment in segments:
        segment = segment.strip()
        # 曜日指定が含まれるかチェック（例: "月火: "）
        match = re.match(r'([月火水木金土日平]+)(?:曜日|):(.+)', segment)
        if match:
            days_str = match.group(1)
            hours_part = match.group(2).strip()
            
            is_today_in_segment = False
            if "平日" in days_str: # 平日指定
                if current_weekday >= 0 and current_weekday <= 4: # 月〜金
                    is_today_in_segment = True
            elif "土日" in days_str and (current_weekday == 5 or current_weekday == 6): # 土日指定
                 is_today_in_segment = True
            else: # 個別の曜日指定（例: 月火）
                for char_day in days_str:
                    if char_day == "月" and current_weekday == 0: is_today_in_segment = True
                    elif char_day == "火" and current_weekday == 1: is_today_in_segment = True
                    elif char_day == "水" and current_weekday == 2: is_today_in_segment = True
                    elif char_day == "木" and current_weekday == 3: is_today_in_segment = True
                    elif char_day == "金" and current_weekday == 4: is_today_in_segment = True
                    elif char_day == "土" and current_weekday == 5: is_today_in_segment = True
                    elif char_day == "日" and current_weekday == 6: is_today_in_segment = True
                    if is_today_in_segment: break
            
            if is_today_in_segment:
                target_hours_str = hours_part # 今日の曜日に特化した時間帯を適用
                break # 今日の曜日が見つかったら他のセグメントは無視
        
    # 曜日指定が見つからなかった場合、または単一の時間帯記述の場合
    if target_hours_str is None:
        # 曜日指定がない、または単一の時間帯記述の場合（例: "11:00-22:00"）
        target_hours_str = opening_hours_str.split(';')[0].strip() # 最初のセグメントを汎用とする

    # 時間帯の解析
    time_ranges = target_hours_str.split(',')
    
    for time_range_str in time_ranges:
        time_range_str = time_range_str.strip()
        if not time_range_str:
            continue

        try:
            start_time_str, end_time_str = time_range_str.split('-')
            start_hour, start_minute = map(int, start_time_str.split(':'))
            end_hour, end_minute = map(int, end_time_str.split(':'))

            start_time = datetime.time(start_hour, start_minute)
            end_time = datetime.time(end_hour, end_minute)

            # 日付をまたぐ営業時間（例: 22:00-02:00）の処理
            if start_time > end_time:
                # 現在時刻が開始時刻以降（今日）または終了時刻以前（翌日）
                # 翌日の時間帯は、現在時刻が00:00から終了時刻の間であれば営業中と判断
                if current_time >= start_time or current_time < end_time:
                    return True, "営業中"
            else:
                # 通常の営業時間
                if start_time <= current_time <= end_time:
                    return True, "営業中"
        except ValueError:
            # 時間形式のパースエラーの場合
            continue # この時間帯はスキップして次を試す

    return False, "営業時間外"


def init_database():
    with app.app_context():
        db.create_all()
        if Shop.query.count() == 0:
            shops_to_insert = [
                Shop("清六屋筑波大学店", "茨城県つくば市天久保3丁目4-8", 36.1059651, 140.1004531, "非対応", "00:00-24:00", "無し")
            ]
            db.session.add_all(shops_to_insert)
            db.session.commit()
            print("初期データを投入しました。")
        else:
            print("データベースには既にデータが存在します。")

with app.app_context():
    init_database()

@app.route('/')
def index():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y年%m月%d日 %H時%M分")
    return render_template('index.html', current_datetime=formatted_time)

@app.route('/api/shops')
def get_shops():
    shops = Shop.query.all()
    shops_data = []
    current_datetime = datetime.datetime.now() # 現在日時を一度取得
    for shop in shops:
        is_open, status_text = is_shop_currently_open(shop.opening_hours, shop.regular_holidays, current_datetime)
        shops_data.append({
            'id': shop.id,
            'name': shop.name,
            'address': shop.address,
            'lat': shop.lat,
            'lng': shop.lng,
            'cashless': shop.cashless,
            'opening_hours': shop.opening_hours,
            'regular_holidays': shop.regular_holidays, 
            'is_open': is_open, 
            'open_status_text': status_text 
        })
    return jsonify(shops_data)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        lat = float(request.form['lat'])
        lng = float(request.form['lng'])
        cashless = request.form['cashless']
        opening_hours = request.form.get('opening_hours', None)
        regular_holidays = request.form.get('regular_holidays', None)

        shop = Shop(name=name, address=address, lat=lat, lng=lng, cashless=cashless,
                    opening_hours=opening_hours, regular_holidays=regular_holidays)
        db.session.add(shop)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_shop.html')

@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_shop(id):
    shop = Shop.query.get_or_404(id)
    db.session.delete(shop)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
