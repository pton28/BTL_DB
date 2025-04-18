import psycopg2
from psycopg2.extras import RealDictCursor
from website.config import Config

def get_db_connection():
    try:
        conn = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
        print("Kết nối cơ sở dữ liệu thành công!")
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def close_db_connection(conn, cursor=None):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Hàm kiểm tra email đã tồn tại chưa
def check_email_exists(email):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM \"USER\" WHERE Email = %s", (email,))
        exists = cur.fetchone() is not None
        return exists
    finally:
        close_db_connection(conn, cur)

# Hàm đăng ký người dùng
def register_user(first_name, last_name, email, password, phone_number, date_of_birth):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        # Thêm người dùng vào bảng USER
        cur.execute(
            """
            INSERT INTO "USER" (FirstName, LastName, Email, "Password", DateOfBirth)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING UserID
            """,
            (first_name, last_name, email, password, date_of_birth)
        )
        user_id = cur.fetchone()['userid']
        
        # Thêm số điện thoại vào bảng USER_PHONE
        cur.execute(
            """
            INSERT INTO USER_PHONE (UserID, PhoneNumber)
            VALUES (%s, %s)
            """,
            (user_id, phone_number)
        )
        
        # Thêm người dùng vào bảng NonAdmin
        cur.execute(
            """
            INSERT INTO NonAdmin (UserID)
            VALUES (%s)
            """,
            (user_id,)
        )
        
        # Tạo CartID và thêm vào bảng VENDEE_AND_CART
        cur.execute(
            """
            INSERT INTO VENDEE_AND_CART (UserID, TotalSpending, CartID)
            VALUES (%s, %s, %s)
            """,
            (user_id, 0.00, user_id)  # CartID tạm thời dùng UserID
        )
        
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Error registering user: {e}")
        conn.rollback()
        return None
    finally:
        close_db_connection(conn, cur)

# Hàm đăng nhập
def login_user(email, password):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT UserID, FirstName, LastName, Email
            FROM "USER"
            WHERE Email = %s AND "Password" = %s
            """,
            (email, password)
        )
        user = cur.fetchone()
        return user
    finally:
        close_db_connection(conn, cur)

# Hàm lấy danh sách sản phẩm (đã có từ trước, giữ nguyên)
def get_products():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (p.ProductID)
                p.ProductID AS productid,
                p.Description AS name,
                pv.Price AS price,
                (SELECT pi.Images 
                 FROM PRODUCT_IMAGES pi 
                 WHERE pi.ProductID = p.ProductID 
                 LIMIT 1) AS image
            FROM PRODUCT p
            LEFT JOIN PRODUCT_VARIANT pv ON p.ProductID = pv.ProductID
            WHERE pv.StockQuantity > 0  
            ORDER BY p.ProductID, pv.ProductID
        """)
        products = cur.fetchall()
        return [
            {
                'id': product['productid'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image']
            }
            for product in products
        ]
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []
    finally:
        close_db_connection(conn, cur)

# Hàm lấy sản phẩm theo UserID
def get_products_by_userid(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT ShopID FROM shop WHERE UserID = %s", (user_id,))
        shop = cur.fetchone()
        if not shop:
            return None

        shop_id = shop['shopid']

        cur.execute("""
            SELECT p.ProductID, p.Description AS name, pv.Price AS price,
                   (SELECT pi.Images FROM PRODUCT_IMAGES pi WHERE pi.ProductID = p.ProductID LIMIT 1) AS image
            FROM PRODUCT p
            LEFT JOIN PRODUCT_VARIANT pv ON p.ProductID = pv.ProductID
            WHERE p.ShopID = %s AND pv.StockQuantity > 0
        """, (shop_id,))

        products = cur.fetchall()
        return products
    except Exception as e:
        print(f"Error fetching producst: {e}")
        return []
    finally:
        close_db_connection(conn, cur)

# Hàm lấy sản phẩm theo ID (đã có từ trước, giữ nguyên)
def get_product_by_id(product_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
        product = cur.fetchone()
        return product
    finally:
        close_db_connection(conn, cur)

# Hàm truy xuất shop của UserID 
def get_shop_by_user_id(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM shop WHERE userid = %s", (user_id,))
        shop = cur.fetchone()
        
        if shop:
            return shop
        return None
    finally:
        close_db_connection(conn, cur)

# Đăng ký shop cho UserID chưa có shop
def reg_shop(user_id, name, address, income, tax_number, phone_num):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO VOUCHER_CREATOR
            DEFAULT VALUES RETURNING creatorid; 
            """
        )
        creator_id = cur.fetchone()['creatorid']

        cur.execute(
            """
            INSERT INTO VENDER (UserID, Income, TaxNumber, CreatorId)
            VALUES (%s, %s, %s, %s) RETURNING UserID
            """, 
            (user_id, income, tax_number, creator_id)
        )
        vender_user_id = cur.fetchone()['userid']

        cur.execute(
            """
            INSERT INTO shop (Address, PhoneNumber, "Name", UserID) 
            VALUES (%s, %s, %s, %s) RETURNING ShopID
            """,
            (address, phone_num, name, vender_user_id)
        )
        shop_id = cur.fetchone()['shopid'] 

        conn.commit()
        return shop_id
    except Exception as e:
        print(f"Gặp lỗi khi đăng ký {e}")
        conn.rollback()
        return None
    finally:
        close_db_connection(conn, cur)
        
# Hàm tạo đơn hàng (đã có từ trước, giữ nguyên)
# def create_order(user_id):
#     conn = get_db_connection()
#     if not conn:
#         return None
#     try:
#         cur = conn.cursor()
#         cur.execute("CALL create_order(%s, NULL)", (user_id,))
#         conn.commit()
#         cur.execute("SELECT currval(pg_get_serial_sequence('orders', 'order_id'))")
#         order_id = cur.fetchone()['currval']
#         return order_id
#     finally:
#         close_db_connection(conn, cur)

# # Hàm thêm chi tiết đơn hàng (đã có từ trước, giữ nguyên)
# def add_order_detail(order_id, product_id, quantity, unit_price):
#     conn = get_db_connection()
#     if not conn:
#         return False
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "INSERT INTO order_details (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
#             (order_id, product_id, quantity, unit_price)
#         )
#         conn.commit()
#         return True
#     except Exception as e:
#         print(f"Error adding order detail: {e}")
#         conn.rollback()
#         return False
#     finally:
#         close_db_connection(conn, cur)
