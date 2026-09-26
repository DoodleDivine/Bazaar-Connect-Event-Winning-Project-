import json
import os
from flask import Flask, render_template, jsonify, request, session, redirect
from werkzeug.utils import secure_filename
import bcrypt
from datetime import datetime, timedelta

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

## Create your own secret key
app.secret_key = "" 

UploadFolder = os.path.join(app.static_folder, 'productuploads')

app.config['UPLOADFOLDER'] = UploadFolder

## Login pages
@app.route('/')
def Index():
    return render_template('pages/index.html')

@app.route('/Register')
def Register():
    return render_template('auth/register.html')

## The Place where file locations are stored.
BaseDIR = os.path.dirname(os.path.abspath(__file__))
DataFile = os.path.join(BaseDIR, 'User.json')
OrderFile = os.path.join(BaseDIR,'Orders.json')
ProductFile = os.path.join(BaseDIR, 'Products.json')

## register data save logic
@app.route("/api/register", methods=["POST"])
def api_Register():
    data = request.get_json()

    RawPassword = data.get("PASS")
    EmailCheck = data.get("EMAIL")

    ## Preventing errors
    try:

        if os.path.exists(DataFile) and os.path.getsize(DataFile) > 0:
            with open(DataFile, "r") as f:
                DataBox = json.load(f)
        else:
            DataBox = []

        for user in DataBox:
            if user['email'] == EmailCheck:
                return jsonify({
                    "success": False,
                    "message": "Please change emails, this one has already been registered."
                })
        
        EncryptedPassword = bcrypt.hashpw(RawPassword.encode("utf-8"), bcrypt.gensalt())

        userData = {
        "name": data.get("NAME"),
        "email": EmailCheck,
        "password": EncryptedPassword.decode("utf-8"),
        "role": data.get("ROLE")
    }
        
        DataBox.append(userData)

        with open(DataFile, "w") as f:
            json.dump(DataBox, f, indent=4)
        
        return jsonify({"success": True,
                        "message": "User Credentials Saved!"})
    except Exception as e:

        print(f"Error: {e}")
        return jsonify({"success": False,
                        "message": "User Credentials Not Saved.."})


@app.route('/Login')
def Login():
    return render_template('auth/login.html')

## login data save logic
@app.route("/api/Login", methods=["POST"])
def api_Login():
    data = request.get_json()

    EmailInput = data.get("EMAILPASS")
    PasswordInput = data.get("LOGINPASS")

    if not os.path.exists(DataFile):
        return jsonify({"success": False,
                        "message": "User Credentials Not Found."})
    
    try:
        with open(DataFile, "r") as f:
            DataBox = json.load(f)

            user_found = None

            for user in DataBox:
                if user['email'] == EmailInput:
                    user_found = user
                    break
            
            if user_found:
                EncryptedPassword = user_found['password'].encode("utf-8")
                LoginPasswordInBytes = PasswordInput.encode("utf-8")

                if bcrypt.checkpw(LoginPasswordInBytes, EncryptedPassword):

                    session['email'] = user_found['email']
                    session['name'] = user_found['name']
                    session['role'] = user_found.get('role')

                    return jsonify({"success": True,
                                    "message": f"Login Successful. Welcome, {user_found['name']}.",
                                    "role": session['role']})
                else:
                    return jsonify({"success": False,
                                    "message": "Invalid Password. Please try again"})
            else:
                return jsonify({"success": False,
                                "message": "Invalid Email not found. Please try again"})
    except Exception as e:

        print(f"Error during login. {e}")
        return jsonify({"success": False,
                        "message": "Internal Server Error."})


## logout the user
@app.route('/api/Logout', methods=["POST"])
def api_Logout():
    session.clear()
    return jsonify({"success": True,
                    "message": "User has logged out successfully!"})

@app.route('/About')
def About():
    return render_template('pages/about.html')


@app.route('/ContactUs')
def Contact():
    return render_template('pages/contact.html')

@app.route('/DonorDashboard')
def DonorDashboard():
    if 'name' not in session or session.get('role') != 'donor':
        return redirect('/Login')
    
    all_products = GetAllProducts()
    product_my_count = len([p for p in all_products if p.get('DonorName') == session['name']])

    order_count = 0

    if os.path.exists(OrderFile) and os.path.getsize(OrderFile) > 0:
        with open(OrderFile)  as f:
            allOrders = json.load(f)
            order_count = len([o for o in allOrders if o.get('donorEmail') == session['email']])
    
    return render_template('pages/donor-dashboard.html', user_name=session['name'], product_count=product_my_count, total_orders=order_count)

@app.route('/AddProducts')
def AddProducts():
    return render_template('pages/add-products.html')

@app.route('/api/AddProducts', methods=["POST"])
def api_AddProducts():
    productName = request.form.get('productName')
    price = request.form.get('price')
    Stock = request.form.get('stock')
    PhoneNumber = request.form.get('phonenumber')
    Description = request.form.get('description')
    imageFile = request.files.get('productImage')

    if imageFile:
        try:
            imageFileName = secure_filename(imageFile.filename)
            imageFilePath = os.path.join(app.config['UPLOADFOLDER'], imageFileName)

            if not os.path.exists(app.config['UPLOADFOLDER']):
                os.makedirs(app.config['UPLOADFOLDER'])
            imageFile.save(imageFilePath)

            if os.path.exists(ProductFile) and os.path.getsize(ProductFile) > 0:
                with open(ProductFile, "r") as f:
                    ProductList = json.load(f)
            else:
                ProductList = []

            ExpiryHours = float(request.form.get('expiryHours'))

            ExpiryTimeStamp = (datetime.now() + timedelta(hours=ExpiryHours)).isoformat()

            NewProduct = {
                "ProductName": productName,
                "Price": price,
                "Stock": Stock,
                "description": Description,
                "phonenumber": PhoneNumber,
                "expirytime": ExpiryTimeStamp,
                "ViewProduct": f"/static/productuploads/{imageFileName}",
                "DonorName": session.get('name'),
                "DonorEmail": session.get('email')
            }

            ProductList.append(NewProduct)

            with open(ProductFile, "w") as f:
                json.dump(ProductList, f, indent=4)

            return jsonify({"success": True,
                            "message": "New Product Saved!"})

        except Exception as e:
            return jsonify({"success": False,
                            "message": "Internal Server Error"})
        
    return jsonify({"success": False,
                    "message": "No Image Uploaded"})

## Signed in Page routes
@app.route('/ReceiverDashboard')
def ReceiverDashboard():
    if 'name' not in session or session.get('role') != 'receiver':
        return redirect('/Login')
    
    products = GetAllProducts()
    
    return render_template('pages/receiver-dashboard.html', user_name=session['name'], products=products)

@app.route('/DonorReports')
def DonorReports():
    if 'name' not in session:
        return redirect('/Login')

    return render_template('pages/donor-reports.html')

@app.route('/ReceiverReports')
def ReceiverReports():
    if 'name' not in session:
        return redirect('/Login')
    
    return render_template('pages/receiver-reports.html')

@app.route('/ReceiverOrders')
def ReceiverOrders():
    if 'name' not in session:
        return redirect('/Login')
    
    if os.path.exists(OrderFile) and os.path.getsize(OrderFile) > 0:
        with open(OrderFile, "r") as f:
            AllOrders = json.load(f)
        
        myOrders = [o for o in AllOrders if o.get('receiverEmail') == session['email']]
    else:
        myOrders = []
    
    return render_template('pages/receiver-orders.html', orders=myOrders)

@app.route('/DonorOrders')
def DonorOrders():
    if 'name' not in session:
        return redirect('/Login')
    
    if os.path.exists(OrderFile) and os.path.getsize(OrderFile) > 0:
        with open(OrderFile, "r") as f:
            AllOrders = json.load(f)
        
        myOrders = [o for o in AllOrders if o.get('donorEmail') == session['email']]
    else:
        myOrders = []
    
    return render_template('pages/donor-orders.html', orders=myOrders)

## This gets all products from Products.json
def GetAllProducts():
    if os.path.exists(ProductFile) and os.path.getsize(ProductFile) > 0:
        with open(ProductFile, "r") as f:
            all_products = json.load(f)
        
        now = datetime.now().isoformat()

        UnExpiredProducts = [p for p in all_products if p.get('expirytime', now) > now]

        if len(UnExpiredProducts) != len(all_products):
            with open(ProductFile, "w") as f:
                json.dump(UnExpiredProducts, f, indent=4)

        return UnExpiredProducts
    return []

## Other pages
@app.route('/DonorProducts')
def DonorProducts():
    if 'name' not in session:
        return redirect('/Login')
    
    all_products = GetAllProducts()
    
    my_products = [p for p in all_products if p.get('DonorName') == session['name']]

    return render_template('pages/donor-products.html', user_name=session['name'], products=my_products)

@app.route('/ReceiverProducts')
def ReceiverProducts():
    if 'name' not in session:
        return redirect('/Login')
    
    products = GetAllProducts()
    
    return render_template('pages/receiver-products.html', products=products)

@app.route('/api/DeleteProduct', methods=["POST"])
def api_DeleteProduct():
    if 'name' not in session:
        return jsonify({"success": False,
                        "message": "Unauthorized"})
    
    ProductToDelete =  request.get_json().get('name')

    try:
        with open(ProductFile, "r") as f:
            products = json.load(f)

        UpdatedProducts = [p for p in products if not (p['ProductName'] == ProductToDelete and p['DonorName'] == session['name'])]

        with open(ProductFile, "w") as f:
            json.dump(UpdatedProducts, f, indent=4)

        return jsonify({"success": True,
                        "message": "Product Deleted!"})
    
    except Exception as e:
        return jsonify({"success": False,
                        "message": str(e)})
    
@app.route('/api/CreateOrder', methods=["POST"])
def api_CreateOrder():
    if 'email' not in session:
        return jsonify({"success": False,
                        "message": "Unauthorized"})
    
    data = request.get_json()

    try:
        if os.path.exists(OrderFile) and os.path.getsize(OrderFile) > 0:
            with open(OrderFile, "r") as f:
                OrdersData = json.load(f)
        else:
            OrdersData = []
        
        NewOrder ={
            "orderID": datetime.now().strftime("%Y%m%d%H%M%S"),
            "productName": data.get('productName'),
            "price": data.get('productPrice'),
            "donorEmail": data.get('donorEmail'),
            "receiverEmail": session['email'],
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }

        OrdersData.append(NewOrder)

        with open(OrderFile, "w") as f:
            json.dump(OrdersData, f, indent=4)
        
        return jsonify({"success": True,
                        "message": "Order Placed Successfully!"})
    except Exception as e:
        return jsonify({"success": False,
                        "message": str(e)})
        
@app.route('/api/UpdateOrderStatus', methods=["POST"])
def api_UpdateOrderStatus():

    data = request.get_json()

    Order_ID = data.get('orderID')
    New_Status = data.get('status')

    try:
        if not os.path.exists(OrderFile) or os.path.getsize(OrderFile) == 0:
            return jsonify({"success": False,
                            "message": "No orders found in the system.."})
    
        with open(OrderFile, "r") as f:
            orders = json.load(f)


        found = False # Flag

        for order in orders:
            if order.get('orderID') == Order_ID:
                order['status'] = New_Status
                found = True
                break
        
        if not found:
            return jsonify({"success": False,
                            "message": "Order ID not found.."})

        with open(OrderFile, "w") as f:
            json.dump(orders, f, indent=4)

        return jsonify({"success": True,
                        "message": f"Order Marked as {New_Status}!"})
    
    except Exception as e:
        return jsonify({"success": False,
                        "message": f"Database Error: {str(e)}"})



if __name__ == "__main__":
    app.run(debug=True, port=8000)
