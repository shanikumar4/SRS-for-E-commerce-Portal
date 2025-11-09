from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import re, json
from .models import products, productImage, CartItem, Order, OrderItem
from django.utils import timezone
from django.db.models import Sum, Count

# from PIL import Image
from app.function import (
    validate_email,
    validate_pass,
    FirstName,
    LastName,
    validate_dob,
    validate_add,
    validate_phoneNo,
    validate_gender,
    validate_id,
    validate,
    validate_dis,
    updateUserDetails,
    updateProductDetails,
    validateprice,
    validateimage,
)
from app.models import User
from django.forms.models import model_to_dict
from django import forms


def gender(request):
    if request.method == "GET":
        data = ["Male", "Female", "Other"]
        return JsonResponse({"gender": data}, status=200)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def productCategory(request):
    if request.method == "GET":
        data = ["Amber", "Floral", "Fresh", "Woody"]
        return JsonResponse({"flavour": data}, status=200)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def signupview(request):
    if request.method == "POST":

        if not request.body.strip():
            return JsonResponse({"Error": "Please provide user information to sign up."}, status=400)

        # data = json.loads(request.body)

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phoneNo = request.POST.get("phone_No")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        conf_password = request.POST.get("Confirm_password")
        profileImg = request.FILES.get("image")

        gendervalidate = validate_gender(gender)

        if (
            password
            and email
            and first_name
            and conf_password
            and phoneNo
            and gender
            # and profileImg
        ):
            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {"msg": "An account with this email already exists."}, status=409
                )

            if password != conf_password:
                return JsonResponse(
                    {"msg": "Password and confirm password both must be same"},
                    status=400,
                )

            if not validate_phoneNo(phoneNo):
                return JsonResponse({"msg": "Please enter a valid phone number."}, status=400)

            if gendervalidate is None:
                return JsonResponse(
                    {"msg": "Invalid gender. Please select 'Male', 'Female', or 'Other'."}, status=400
                )

            if not validate_pass(password):
                return JsonResponse(
                    {
                        "msg": "Password must be at least 6 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."
                    },
                    status=400,
                )
            if not validate_email(email):
                return JsonResponse(
                    {"msg": "A valid email address is required."}, status=400
                )
            if not FirstName(first_name):
                return JsonResponse(
                    {
                        "msg": "First name is required and must contain only letters."
                    },
                    status=400,
                )
            if not LastName(last_name):
                return JsonResponse(
                    {"msg": "Last name must contain only letters."}, status=400
                )
            else:

                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_No=phoneNo,
                    gender=gendervalidate,
                    profileImage=profileImg,
                )

                user.set_password(password)
                user.save()

                return JsonResponse({"msg": "User registered successfully."}, status=201)

        else:
            return JsonResponse({"msg": "Please fill in all required fields."}, status=400)
    else:

        return JsonResponse({"msg": "Method not allowed"}, status=405)


def loginview(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "Please provide an email and password."}, status=400)

        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if request.user.is_authenticated:
            return JsonResponse({"msg": "You are already logged in. "}, status=200)

        if not email or not password:
            return JsonResponse(
                {"msg": "Email and password are required."}, status=400
            )

        user = authenticate(request=request, email=email, password=password)

        if user is not None:
            login(request, user)

            userType = "user"

            if user.is_superuser:
                userType = "admin"

            return JsonResponse(
                {"msg": "You are now logged in.", "user": userType}, status=200
            )

        else:
            return JsonResponse({"msg": "Invalid email or password."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def updateUser(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "Please provide the information you wish to update."}, status=400)

        # data = json.loads(request.body)

        currentUser = request.user
        userid = currentUser.id

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phoneNo = request.POST.get("phone_No")
        gender = request.POST.get("gender")
        profileImg = request.FILES.get("profileImage")

        if not User.objects.filter(id=userid).exists():
            return JsonResponse({"msg": "User not found."}, status=404)

        if currentUser.is_authenticated:

            if updateUserDetails(
                first_name,
                last_name,
                gender,
                phoneNo,
                profileImg,
                userid,
            ):
                return JsonResponse(
                    {"msg": "Your profile has been updated successfully."}, status=200
                )
            else:
                return JsonResponse({"msg": "No valid details were provided for an update."}, status=400)

        else:
            return JsonResponse({"msg": "You must be logged in to update your profile."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def logoutview(request):
    if request.method == "DELETE":
        if request.user.is_authenticated:

            logout(request)
            return JsonResponse({"msg": "You have been logged out successfully."}, status=200)
        else:
            return JsonResponse({"msg": "You are not logged in."}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def userdetails(request):
    user = request.user
    if request.method == "GET":

        if user.is_authenticated:

            # imgUrl = user.profileImage.url

            columns = [
                "first_name",
                "last_name",
                "email",
                "phone_No",
                "date_of_birth",
                "gender",
            ]

            data = model_to_dict(user, fields=columns)
            if user.profileImage:
                data["image_url"] = user.profileImage.url
            else:
                data["image_url"] = None

            return JsonResponse(data, status=200)
        else:
            return JsonResponse({"msg": "You must be logged in to view your details."}, status=401)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def addproduct(request):
    if request.method == "POST":

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "You do not have permission to perform this action."}, status=400)

        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category = request.POST.get("category")

        images = request.FILES.getlist("image")

        if "image" in request.FILES["image"].content_type != " image/jpeg":
            return JsonResponse({"msg": "Invalid image format. Only JPEG images are allowed."}, status=400)

        categoryItem = ["Amber", "Floral", "Fresh", "Wooy"]

        if not category in categoryItem:
            return JsonResponse({"msg": "Invalid category. Please select from 'Amber', 'Floral', 'Fresh', or 'Woody'."}, status=400)
        if not validateprice(price):
            return JsonResponse({"msg": "Invalid price. Please enter a valid number."}, status=400)
        if not validateprice(stock):
            return JsonResponse({"msg": "Invalid stock. Please enter a valid number."}, status=400)
        if not validate(name):
            return JsonResponse({"msg": "A valid product name is required."}, status=400)
        if not validate_dis(description):
            return JsonResponse({"msg": "A valid product description is required."}, status=400)

        if request.user.is_authenticated:
            if name and description:
                product = products(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    category=category,
                )
                product.save()

                for image in images:
                    productImage.objects.create(products=product, image=image)

                return JsonResponse({"msg": "Product added successfully."}, status=201)
            else:
                return JsonResponse(
                    {"msg": "Please provide all required product details (name, description, price, stock)."}, status=400
                )
        else:
            return JsonResponse({"msg": "You must be logged in to perform this action."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def updateProduct(request):
    if request.method == "POST":

        if not request.body.strip():
            return JsonResponse({"msg": "Please provide the product details you wish to update."}, status=400)

        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        images = request.FILES.get("image")
        updateid = request.POST.get("id")
        productImgId = request.POST.get("productImgId")
        category = request.POST.get("category")

        categoryItem = ["Amber", "Floral", "Fresh", "Woody"]

        if not category in categoryItem:
            return JsonResponse({"msg": "Invalid category. Please select from 'Amber', 'Floral', 'Fresh', or 'Woody'."}, status=400)
        if not validateprice(price):
            return JsonResponse({"msg": "Invalid price. Please enter a valid number."}, status=400)
        if not validateprice(stock):
            return JsonResponse({"msg": "Invalid stock. Please enter a valid number."}, status=400)
        if not validate(name):
            return JsonResponse({"msg": "A valid product name is required."}, status=400)
        if not validate_dis(description):
            return JsonResponse({"msg": "A valid product description is required."}, status=400)

        if validate_id(updateid):
            return JsonResponse({"msg": "A product ID is required to update."}, status=400)

        if not products.objects.filter(id=updateid).exists():
            return JsonResponse({"msg": "No product found with this ID."}, status=404)

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "You do not have permission to perform this action."}, status=403)

        if current_user.is_authenticated:

            if updateProductDetails(
                updateid, name, description, price, stock, category
            ):
                if productImgId:
                    img = productImage.objects.get(
                        products_id=updateid, id=productImgId
                    )
                    img.image = images
                    img.save()

                return JsonResponse(
                    {"msg": "Product details updated successfully."}, status=200
                )

            else:
                return JsonResponse({"msg": "Could not update product. No valid details provided."}, status=400)

        else:
            return JsonResponse({"msg": "You must be logged in to perform this action."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def deleteProduct(request):
    if request.method == "DELETE":

        delid = request.GET.get("id")

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "You do not have permission to perform this action."}, status=403)

        if current_user.is_authenticated:

            if not delid:
                return JsonResponse({"msg": "A product ID is required to delete."}, status=400)

            if products.objects.filter(id=delid, active=True):

                products.objects.filter(id=delid).update(
                    active=False, deleteAt=timezone.now()
                )
                return JsonResponse({"msg": "Product has been deleted successfully."}, status = 200)

            else:
                return JsonResponse({"msg": "No active product found with this ID."}, status=404)
        else:
            return JsonResponse({"msg": "You must be logged in to perform this action."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def productDetails(request):

    if request.method == "GET":
        user = request.user

        allProduct = products.objects.filter(active=True)

        data = []

        columns = [
            "name",
            "description",
            "price",
            "stock",
            "category",
            "id",
        ]

        for product in allProduct:
            productdata = model_to_dict(product, fields=columns)

            allproductimg = productImage.objects.filter(products_id=product.id)

            imgurl = [img.image.url for img in allproductimg if img.image]
            productdata["imgurl"] = imgurl
            data.append(productdata)

        return JsonResponse(data, safe=False, status=200)
    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def filterproduct(request):
    if request.method == "GET":
        user = request.user
        filterby = request.GET.get("input", default="all")

        if filterby is None:

            return JsonResponse({"msg": "Please provide a filter category."}, status=400)

        if user.is_authenticated:
            category = ["Amber", "Floral", "Fresh", "Woody"]
            if filterby in category:
                allProduct = products.objects.filter(active=True, category=filterby)
            if re.match("^[0-9]*$", filterby):
                allProduct = products.objects.filter(active=True, price=filterby)

            if filterby == "all":
                allProduct = products.objects.filter(active=True)

            data = []

            columns = [
                "name",
                "description",
                "price",
                "stock",
                "category",
                "id",
            ]
            for product in allProduct:
                productdata = model_to_dict(product, fields=columns)

                allproductimg = productImage.objects.filter(products_id=product.id)

                imgurl = [img.image.url for img in allproductimg if img.image]
                productdata["imgurl"] = imgurl
                data.append(productdata)

            return JsonResponse(data, safe=False, status=200)
        else:
            return JsonResponse({"msg": "You must be logged in to view products."}, status=401)
    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def addtocart(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "Please provide a product ID and quantity."}, status=400)

        user = request.user

        # data = json.loads(request.body)
        productid = request.POST.get("productid")
        quantity = request.POST.get("quantity")

        if products.objects.filter(id=productid, active=False):
            return JsonResponse({"msg": "This product does not exist or is no longer available."}, status=404)

        product = products.objects.filter(id=productid).values("stock")
        if quantity is None or quantity == "0" or quantity == 0:
            quantity = 1

        if user.is_authenticated:
            stock = product[0].get("stock")
            stock = int(stock)
            quantity = int(quantity)
            print(stock)
            if quantity > stock:
                return JsonResponse({"msg": "The requested quantity is not available in stock."}, status=400)
            newstock = int(stock) - int(quantity)
            print(newstock)

            if productid is None:
                return JsonResponse({"msg": "A product ID is required to add to cart."}, status=400)

            if productid:
                item = CartItem.objects.create(
                    user_id=user.id, products_id=productid, quantity=quantity
                )

                products.objects.filter(id=productid).update(
                    stock=newstock, updateAt=timezone.now()
                )

                return JsonResponse({"msg": "Product added to your cart."}, status=201)

            else:
                return JsonResponse({"msg": "A product ID is required."}, status=400)

        else:
            return JsonResponse({"msg": "You must be logged in to add items to your cart."}, status=401)

    else:
        return JsonResponse({"msg": "Method Not Allowed."}, status=405)


def cartdata(request):
    if request.method == "GET":

        user = request.user

        if user.is_authenticated:
            cartitems = (
                CartItem.objects.filter(user_id=user.id)
                .select_related("products")
                .prefetch_related("products__productimage_set")
            )
            data = []

            for items in cartitems:
                product = items.products

                productdata = model_to_dict(product, fields=["id", "name", "price"])

                allproductimg = product.productimage_set.all()

                imgurl = [img.image.url for img in allproductimg if img.image]

                itemdata = {
                    "cartiteid": items.id,
                    "quantity": items.quantity,
                    "product": productdata,
                    "images": imgurl,
                }

                data.append(itemdata)

            return JsonResponse(data, safe=False, status=200)

        else:
            return JsonResponse({"msg": "You must be logged in to view your cart."}, status=401)
    else:
        return JsonResponse({"msg": "Method Not Allowed."}, status=405)


def removeFromCart(request):
    if request.method == "DELETE":

        productid = request.GET.get("id")
        if not productid:
            return JsonResponse({"msg": "A product ID is required to remove from cart."}, status=404)

        current_user = request.user

        userid = current_user.id

        if current_user.is_authenticated:
            product = products.objects.filter(id=productid).values("stock")

            if not product:
                return JsonResponse({"msg": "No product found with this ID."}, status=404)
            stock = product[0].get("stock")

            if CartItem.objects.filter(products_id=productid, user_id=userid):
                addstock = CartItem.objects.filter(
                    products_id=productid, user_id=userid
                ).aggregate(sum=Sum("quantity", default=0))

                newstock = stock + addstock.get("sum")

                CartItem.objects.filter(products_id=productid, user_id=userid).delete()

                products.objects.filter(id=productid).update(
                    stock=newstock, updateAt=timezone.now()
                )

                return JsonResponse({"msg": "Product removed from your cart."}, status = 200)

            else:
                return JsonResponse({"msg": "This product is not in your cart."}, status=404)
        else:
            return JsonResponse({"msg": "You must be logged in to modify your cart."}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def order(request):
    if request.method == "POST":

        totalprice = request.POST.get("totalPrice")
        address = request.POST.get("address")
        user = request.user
        userid = user.id

        if not totalprice:
            return JsonResponse({"msg": "Total price is required to place an order."}, status=400)
        if not address:
            return JsonResponse({"msg": "A shipping address is required to place an order."}, status=400)

        if user.is_authenticated:

            cartitem = CartItem.objects.filter(user_id=user.id).select_related(
                "products"
            )

            if not cartitem:
                return JsonResponse({"msg": "Your cart is empty. Please add items before placing an order."}, status=400)

            new_order = Order.objects.create(
                totalPrice=totalprice, shippingAddress=address, user_id=userid
            )

            cartitem = CartItem.objects.filter(user_id=user.id).select_related(
                "products"
            )

            data = []

            for item in cartitem:
                data.append(
                    OrderItem(
                        order=new_order,
                        product=item.products,
                        quantity=item.quantity,
                        price=item.products.price,
                        name=item.products.name,
                        shippingAddress=new_order.shippingAddress,
                        status="Confirmed",
                    )
                )

            OrderItem.objects.bulk_create(data)

            CartItem.objects.filter(user_id=userid).delete()

            orederitem = OrderItem.objects.filter(order_id=new_order)

            orderdetails = []

            columns = [
                "name",
                "quantity",
                "price",
                "shippingAddress",
                "status",
            ]

            for item in orederitem:
                productdata = model_to_dict(item, fields=columns)
                orderdetails.append(productdata)

            return JsonResponse(orderdetails, safe=False, status=200)

            # return JsonResponse({"msg": "Order Placed"}, status=200)
        else:
            return JsonResponse({"msg": "You must be logged in to place an order."}, status=401)
    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


def salesInsights(request):
    if request.method == "GET":

        productid = request.GET.get("id")

        if not productid:
            return JsonResponse({"msg": "A product ID is required to view insights."}, status=400)

        user = request.user

        if user.is_authenticated:

            product = products.objects.filter(id=productid)

            revenue = OrderItem.objects.filter(product_id=productid).aggregate(
                Sum("price")
            )

            totalsales = OrderItem.objects.filter(product_id=productid).aggregate(
                Sum("quantity")
            )

            numberOfOrders = OrderItem.objects.filter(product_id=productid).aggregate(
                Count("product_id")
            )

            print(revenue)
            print(totalsales)
            print(numberOfOrders)
