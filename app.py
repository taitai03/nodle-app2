import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    def __init__(self, name, address, lat, lng, cashless):
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.cashless = cashless

    def __repr__(self):
        return f"<Shop(name='{self.name}', address='{self.address}')>"

def init_database():
    with app.app_context():
        db.create_all()
        if Shop.query.count() == 0:
            shops_to_insert = [
                Shop("清六屋筑波大学店", "茨城県つくば市天久保3丁目4-8", 36.1059651, 140.1004531, "非対応")
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
    return render_template('index.html')

@app.route('/api/shops')
def get_shops():
    shops = Shop.query.all()
    return jsonify([
        {
            'id': shop.id,
            'name': shop.name,
            'address': shop.address,
            'lat': shop.lat,
            'lng': shop.lng,
            'cashless': shop.cashless
        } for shop in shops
    ])

@app.route('/admin/add', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        lat = float(request.form['lat'])
        lng = float(request.form['lng'])
        cashless = request.form['cashless']
        shop = Shop(name=name, address=address, lat=lat, lng=lng, cashless=cashless)
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
    app.run(debug=True)