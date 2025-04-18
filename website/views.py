from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from website.models import get_products, get_product_by_id, get_shop_by_user_id, reg_shop, get_products_by_userid, get_cart, get_user_info, get_user_addresses, add_to_cart_func, add_user_address, delete_user_address, update_user_address, set_default_address, delete_from_cart_func, create_order, add_order_detail, update_vendee_spending, update_vender_income, update_product_stock, get_vender_id_by_product
from decimal import Decimal

views = Blueprint('views', __name__)

# Thêm route cho việc truy cập trang chủ
@views.route('/')
def home():
    products = get_products()
    
    return render_template('home.html', products=products)

# Thêm route cho thông tin cá nhân
@views.route('/info_user')
def info_user():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem thông tin cá nhân', 'error')
        return redirect(url_for('auth.login'))

    user_info = get_user_info(session['user_id'])
    addresses = get_user_addresses(session['user_id'])
    return render_template('info_user.html', user_info=user_info, addresses=addresses)

# Thêm route cho việc thêm địa chỉ
@views.route('/info_user/add_address', methods=['POST'])
def add_address():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để thêm địa chỉ', 'error')
        return redirect(url_for('auth.login'))

    home_number = request.form.get('home_number')
    street = request.form.get('street')
    district = request.form.get('district')
    city = request.form.get('city')
    province = request.form.get('province')
    is_default = request.form.get('is_default') == 'on'

    if not all([home_number, street, district, city, province]):
        flash('Vui lòng điền đầy đủ thông tin địa chỉ', 'error')
        return redirect(url_for('views.info_user'))

    success = add_user_address(session['user_id'], home_number, street, district, city, province, is_default)
    if success:
        flash('Thêm địa chỉ thành công', 'success')
    else:
        flash('Thêm địa chỉ thất bại', 'error')
    return redirect(url_for('views.info_user'))

# Thêm route cho việc xóa địa chỉ
@views.route('/info_user/delete_address', methods=['POST'])
def delete_address():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xóa địa chỉ', 'error')
        return redirect(url_for('auth.login'))

    home_number = request.form.get('home_number')
    street = request.form.get('street')
    district = request.form.get('district')
    city = request.form.get('city')
    province = request.form.get('province')

    success = delete_user_address(session['user_id'], home_number, street, district, city, province)
    if success:
        flash('Xóa địa chỉ thành công', 'success')
    else:
        flash('Xóa địa chỉ thất bại', 'error')
    return redirect(url_for('views.info_user'))

# Thêm route cho việc sửa địa chỉ
@views.route('/info_user/update_address', methods=['POST'])
def update_address():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để sửa địa chỉ', 'error')
        return redirect(url_for('auth.login'))

    old_home_number = request.form.get('old_home_number')
    old_street = request.form.get('old_street')
    old_district = request.form.get('old_district')
    old_city = request.form.get('old_city')
    old_province = request.form.get('old_province')

    new_home_number = request.form.get('home_number')
    new_street = request.form.get('street')
    new_district = request.form.get('district')
    new_city = request.form.get('city')
    new_province = request.form.get('province')

    if not all([old_home_number, old_street, old_district, old_city, old_province, new_home_number, new_street, new_district, new_city, new_province]):
        flash('Vui lòng điền đầy đủ thông tin địa chỉ', 'error')
        return redirect(url_for('views.info_user'))

    success = update_user_address(session['user_id'], old_home_number, old_street, old_district, old_city, old_province, new_home_number, new_street, new_district, new_city, new_province)
    if success:
        flash('Sửa địa chỉ thành công', 'success')
    else:
        flash('Sửa địa chỉ thất bại', 'error')
    return redirect(url_for('views.info_user'))

# Thêm route cho việc thiết lập địa chỉ mặc định
@views.route('/info_user/set_default_address', methods=['POST'])
def set_default():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để thiết lập địa chỉ mặc định', 'error')
        return redirect(url_for('auth.login'))

    home_number = request.form.get('home_number')
    street = request.form.get('street')
    district = request.form.get('district')
    city = request.form.get('city')
    province = request.form.get('province')

    success = set_default_address(session['user_id'], home_number, street, district, city, province)
    if success:
        flash('Thiết lập địa chỉ mặc định thành công', 'success')
    else:
        flash('Thiết lập địa chỉ mặc định thất bại', 'error')
    return redirect(url_for('views.info_user'))

# Thêm route cho việc truy cập trang sản phẩm
@views.route('/product/<int:product_id>')
def product_detail(product_id):
    print(f"Fetching product with ID: {product_id}")  # Debug
    product = get_product_by_id(product_id)
    print(f"Product data: {product}")  # Debug
    if not product:
        return redirect(url_for('views.home'))
    return render_template('product.html', product=product)

# @views.route('/cart/add/<int:product_id>', methods=['POST'])
# def add_to_cart(product_id):
#     if 'user_id' not in session:
#         flash('Please login to add items to cart', 'error')
#         return redirect(url_for('auth.login'))
    
#     product = get_product_by_id(product_id)
#     if not product:
#         flash('Product not found', 'error')
#         return redirect(url_for('views.home'))
    
#     quantity = int(request.form.get('quantity', 1))
#     if quantity > product['stock']:
#         flash('Not enough stock', 'error')
#         return redirect(url_for('views.product_detail', product_id=product_id))
    
#     # Tạo đơn hàng nếu chưa có
#     order_id = create_order(session['user_id'])
#     if not order_id:
#         flash('Failed to create order', 'error')
#         return redirect(url_for('views.product_detail', product_id=product_id))
    
#     # Thêm chi tiết đơn hàng
#     success = add_order_detail(order_id, product_id, quantity, product['price'])
#     if success:
#         flash('Item added to cart', 'success')
#     else:
#         flash('Failed to add item to cart', 'error')
    
#     return redirect(url_for('views.product_detail', product_id=product_id))

# Thêm route cho giỏ hàng
@views.route('/cart')
def cart():
    # if 'user_id' not in session:
    #     flash('Vui lòng đăng nhập để xem giỏ hàng', 'error')
    #     return redirect(url_for('auth.login'))
    # Logic hiển thị giỏ hàng sẽ được thêm sau
    return render_template('cart.html')

# Thêm route cho quản lý cửa hàng
@views.route('/shop_manager')
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

