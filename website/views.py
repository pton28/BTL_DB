from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from website.models import get_products, get_product_by_id, get_shop_by_user_id, reg_shop, get_products_by_userid
# create_order, add_order_detail

views = Blueprint('views', __name__)

@views.route('/')
def home():
    products = get_products()
    return render_template('home.html', products=products)

@views.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('views.home'))
    return render_template('product.html', product=product)

# Thêm route cho giỏ hàng
@views.route('/cart')
def cart():
    # if 'user_id' not in session:
    #     flash('Vui lòng đăng nhập để xem giỏ hàng', 'error')
    #     return redirect(url_for('auth.login'))
    # Logic hiển thị giỏ hàng sẽ được thêm sau
    return render_template('cart.html')

# Kiểm tra tồn tại của shop và đăng kí shop
@views.route('/shop_manager', methods=['GET', 'POST'])
def shop_manager():
    user_id = session.get('user_id')
    if not user_id:
        flash('Vui lòng đăng nhập để quản lý cửa hàng', 'error')
        return redirect(url_for('auth.login'))

    shop = get_shop_by_user_id(user_id)

    if shop:
        products = get_products_by_userid(user_id)
        return render_template('shop_manager.html', shop=shop, products=products)
    return render_template('shop_manager.html', shop=None)

# Đăng ký cửa hàng
@views.route('/reg_shop', methods=['GET', 'POST'])
def reg_shop():
    user_id = session.get('user_id')

    if request.method == 'POST':
        name = request.form['name']
        tax_number = request.form['tax_number']
        address = request.form['address']
        phone_num = request.form['phone_number']
        income = 0

        shop_id = reg_shop(user_id, name, address, income, tax_number, phone_num)
        if shop_id:
            flash('Đăng ký cửa hàng thành công', 'success')
            return redirect(url_for('views.shop_manager'))
        else:
            flash('Đăng ký cửa hàng thất bại', 'error')

    return render_template('reg_shop.html')

# Đăng ký sản phẩm
@views.route('/reg_products')
def reg_products():
    return render_template('reg_products.html')

# Thêm route cho thông tin cá nhân
@views.route('/info_user')
def info_user():
    return render_template('info_user.html')