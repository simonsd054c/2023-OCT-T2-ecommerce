from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

app = Flask(__name__)

# connect to the database
                                #       dbms    driver          db_user    db_pass      URL PORT    db_name
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql+psycopg2://ecommerce_dev:123456@localhost:5432/oct_ecommerce"

db = SQLAlchemy(app)

ma = Marshmallow(app)

# Model - table in our database
class Product(db.Model):
    # define tablename
    __tablename__ = "products"
    # define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # more attributes
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class ProductSchema(ma.Schema):
    class Meta:
        # fields
        fields = ("id", "name", "description", "price", "stock")

# to handle all the products
products_schema = ProductSchema(many=True)
# to handle a single product
product_schema = ProductSchema()

# CLI commands
@app.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")

@app.cli.command("seed")
def seed_db():
    # create a product object
    product1 = Product(
        name="Product 1",
        description="Product 1 desc",
        price=140.54,
        stock=15
    )
    product2 = Product()
    product2.name = "Product 2"
    product2.price = 15.99
    product2.stock = 5
    # add to session
    db.session.add(product1)
    db.session.add(product2)
    # commit
    db.session.commit()
    print("Tables seeded")

@app.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")


# route to return all the products
@app.route("/products")
def get_products():
    stmt = db.select(Product) # SELECT * FROM PRODUCTS; /// [["Product 1", "Product 2", ...]]
    products_list = db.session.scalars(stmt) # ["Product 1", "Product 2", ...]
    # convert non-seriazible to JSON (readable format)
    data = products_schema.dump(products_list)
    return data

# hanlde a single product
@app.route("/products/<int:product_id>")
def get_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id) # SELECT * FROM PRODUCTS WHERE id=product_id
    product = db.session.scalar(stmt)
    if(product):
        data = product_schema.dump(product)
        return data
    else:
        return {"error": f"Product with id {product_id} doesn't exist"}, 404
    
@app.route("/products", methods=["POST"])
def create_product():
    product_fields = request.get_json()
    print(product_fields)
    new_product = Product(
        name=product_fields.get("name"),
        description=product_fields.get("description"),
        price=product_fields.get("price"),
        stock=product_fields.get("stock")
    )
    db.session.add(new_product)
    db.session.commit()
    data = product_schema.dump(new_product)
    return data, 201