from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import re, json
from .models import products, productImage, CartItem, Order, OrderItem
from django.utils import timezone
from django.db.models import Sum
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
        return JsonResponse({"msg": "method not allowed"}, status=405)


def productCategory(request):
    if request.method == "GET":
        data = ["Amber", "Floral", "Fresh", "Woody"]
        return JsonResponse({"flavour": data}, status=200)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)


def signupview(request):
    if request.method == "POST":

        if not request.body.strip():
            return JsonResponse({"Error": "Enter The User Informations"}, status=400)

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
                    {"msg": "User already registered, Please try again!"}, status=409
                )

            if password != conf_password:
                return JsonResponse(
                    {"msg": "Password and confirm_password both must be same"},
                    status=400,
                )

            if not validate_phoneNo(phoneNo):
                return JsonResponse({"msg": "Enter valid phone no"}, status=400)

            if gendervalidate is None:
                return JsonResponse(
                    {"msg": "gender must be MALE or FEMALE or Other"}, status=400
                )

            if not validate_pass(password):
                return JsonResponse(
                    {
                        "msg": "Password is mandtory and Password must contain atleast a Uppercase, a lowercase , a special charcter and a number and minimum length must be 6"
                    },
                    status=400,
                )
            if not validate_email(email):
                return JsonResponse(
                    {"msg": "Email is manadtory and Enter a valid Email"}, status=400
                )
            if not FirstName(first_name):
                return JsonResponse(
                    {
                        "msg": "First name is mandatory and First name must contain only alphabetical"
                    },
                    status=400,
                )
            if not LastName(last_name):
                return JsonResponse(
                    {"msg": "Last name must contain only alphabetical"}, status=400
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

                return JsonResponse({"msg": "User Registerd Successfully"}, status=201)

        else:
            return JsonResponse({"msg": "Enter all required field"}, status=400)
    else:

        return JsonResponse({"msg": "method not allowed"}, status=405)


def loginview(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "Enter The email and password"}, status=400)

        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password") 
        
        if request.user.is_authenticated:
            return JsonResponse({"msg": "User already logged in "}, status=200)

        if not email or not password:
            return JsonResponse(
                {"msg": "email and password both mandatory"}, status=400
            )

        user = authenticate(request=request, email=email, password=password)

        if user is not None:
            login(request, user)

            userType = "user"

            if user.is_superuser:
                userType = "admin"

            return JsonResponse(
                {"msg": "User logged in successfully", "user": userType}, status=200
            )

        else:
            return JsonResponse({"msg": "User or Password is incorrect"}, status=401)

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def updateUser(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "Enter The User Informations"}, status=400)

        # data = json.loads(request.body)

        currentUser = request.user
        userid = currentUser.id

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phoneNo = request.POST.get("phone_No")
        gender = request.POST.get("gender")
        profileImg = request.FILES.get("profileImage")

        if not User.objects.filter(id=userid).exists():
            return JsonResponse({"msg": "id not found"}, status=400)

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
                    {"msg": "user details Updated successfully"}, status=200
                )
            else:
                return JsonResponse({"msg": "details not field"}, status=400)

        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)


def logoutview(request):
    if request.method == "DELETE":
        if request.user.is_authenticated:

            logout(request)
            return JsonResponse({"msg": "you are successfully logout"}, status=200)
        else:
            return JsonResponse({"msg": "User is not login"}, status=400)
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
            return JsonResponse({"msg": "user not login"}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def addproduct(request):
    if request.method == "POST":

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "only admin have access"}, status=400)
        
        
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category = request.POST.get("category")

        images = request.FILES.getlist("image")
        
        # for img in images:
        #      Image.open(img.file)
        #      Image.verify()
             
        #      return JsonResponse({"msg": "invalid image"}, status=400)
                
        
        
        
        categoryItem =  ['Amber','Floral', 'Fresh', 'Woody']
        
        if not category in categoryItem:
             return JsonResponse({"msg": "invalid category"}, status=400)
        if not validateprice(price):
            return JsonResponse({"msg": "invalid price"}, status=400)
        if not validateprice(stock):
            return JsonResponse({"msg": "invalid stock"}, status=400)
        if not validate(name):
            return JsonResponse({"msg": "invalid name"}, status=400)
        if not validate_dis(description):
            return JsonResponse({"msg": "invalid description"}, status=400)
            
        
        
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

                return JsonResponse({"msg": "product added successfully"}, status=201)
            else:
                return JsonResponse(
                    {"msg": "Enter name ,description, price , stock"}, status=400
                )
        else:
            return JsonResponse({"msg": "user is not loged in"}, status=401)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)


def updateProduct(request):
    if request.method == "POST":
        
        if not request.body.strip():
            return JsonResponse({"msg": "Enter The User Informations"}, status=400)

        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")   
        images = request.FILES.get("image")
        updateid = request.POST.get("id")
        productImgId = request.POST.get("productImgId")
        category = request.POST.get("category")

       
        categoryItem =  ['Amber','Floral', 'Fresh', 'Woody']
        
        if not category in categoryItem:
             return JsonResponse({"msg": "invalid category"}, status=400)
        if not validateprice(price):
            return JsonResponse({"msg": "invalid price"}, status=400)
        if not validateprice(stock):
            return JsonResponse({"msg": "invalid stock"}, status=400)
        if not validate(name):
            return JsonResponse({"msg": "invalid name"}, status=400)
        if not validate_dis(description):
            return JsonResponse({"msg": "invalid description"}, status=400)
            
        if validate_id(updateid):
            return JsonResponse({"msg": "id required"}, status=400)

        if not products.objects.filter(id=updateid).exists():
            return JsonResponse({"msg": "id not found"}, status=400)

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "only admin have access"}, status=400)

        if current_user.is_authenticated:

            if updateProductDetails(updateid, name, description, price, stock, category):
                if productImgId:
                    img = productImage.objects.get(products_id=updateid, id=productImgId)
                    img.image = images
                    img.save()

                return JsonResponse(
                    {"msg": "Products details update successfully"}, status=200
                )

            else:
                return JsonResponse({"msg": "product was not found"}, status=400)

        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)


def deleteProduct(request):
    if request.method == "DELETE":

        delid = request.GET.get("id")

        current_user = request.user
        admin = current_user.is_superuser

        if not admin:
            return JsonResponse({"msg": "only admin have access"}, status=400)

        if current_user.is_authenticated:

            if not delid:
                return JsonResponse({"msg": "id required"}, status=400)

            if products.objects.filter(id=delid, active=True):

                products.objects.filter(id=delid).update(
                    active=False, deleteAt=timezone.now()
                )
                return JsonResponse({"msg": "product deleted successfully"})

            else:
                return JsonResponse({"msg": "invalid delid"}, status=400)
        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)


def productDetails(request):
    
    
    if request.method == "GET":
        user = request.user
        
        # if  user.is_superuser==0: 
        #     return JsonResponse({"msg": "only admin can access"}, status=400) 
        
        if user.is_authenticated:

            # imgUrl = user.profileImage.url

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
            return JsonResponse({"msg": "user not login"}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)
    


def filterproduct(request):
     if request.method == "GET":
        user = request.user
        filterby = request.GET.get("input", default = "all")
        
        if filterby is None:
             
            return JsonResponse({"msg": "enter category or price"}, status=400)
        
        
        if user.is_authenticated:
            category = ['Amber','Floral', 'Fresh', 'Woody']
            if filterby in category:
                allProduct = products.objects.filter(active=True, category = filterby)
            if re.match("^[0-9]*$", filterby):
                allProduct = products.objects.filter(active=True, price = filterby)
                
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
            return JsonResponse({"msg": "user not login"}, status=400)
     else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)
    



def addtocart(request):
    if request.method == "POST":
        if not request.body.strip():
            return JsonResponse({"msg": "body can't be null"}, status= 400)
       
        user = request.user
            
        # data = json.loads(request.body) 
        productid = request.POST.get('productid')
        quantity = request.POST.get('quantity')
        
        if products.objects.filter(id=productid, active = False):
            return JsonResponse({"msg": "invalid product id"}, status = 400)
        
        product = products.objects.filter(id = productid).values("stock")
        if quantity is None or quantity=="0" or quantity==0:
         quantity =1 
        
        if user.is_authenticated:    
            stock = product[0].get("stock")
            stock = int(stock)
            quantity=int(quantity)
            print(stock)
            if quantity>stock:
              return JsonResponse({"msg": "product unavaliabe"}, status = 400)
            newstock = int(stock)-int(quantity)
            print(newstock)
            
                
            
            
            if productid is None:
                return JsonResponse({"msg": "product id required"}, status=400)
                
       
      
            
            if productid:
                item = CartItem.objects.create(
                    user_id = user.id,
                    products_id = productid,
                    quantity = quantity
                )
                
                products.objects.filter(id=productid).update(stock=newstock, updateAt = timezone.now())
                
                allProduct = CartItem.objects.filter(user_id = user.id)
                      
                data = []

                columns = [
                    "quantity"
                ]
                
                
                
                

                for product in allProduct:
                    productdata = model_to_dict(product, fields=columns)

                    # allproductimg = productImage.objects.filter(products_id=product.id)

                    # imgurl = [img.image.url for img in allproductimg if img.image]
                    # productdata["imgurl"] = imgurl
                    data.append(productdata)
                    
                    
                newid = allProduct.get("products_id")
                
                print(newid)                    
                    
                

                return JsonResponse(data,safe=False, status=200)
                
                # return JsonResponse(, status=201)
            
            else:
                return JsonResponse({"msg": "enter product id"}, status=201)
        
        else:
             return JsonResponse({"msg": "authentication required"}, status=401)
                       
    else:
         return JsonResponse({"msg": "Method Not Allowed"}, status=405)   
    
    
def removeFromCart(request):
    if request.method == "DELETE":

        productid = request.GET.get("id")

        current_user = request.user
        
        userid = current_user.id

        if current_user.is_authenticated:
            product = products.objects.filter(id = productid).values("stock")
            stock = product[0].get("stock")

            if not productid:
                return JsonResponse({"msg": "id required"}, status=400)

            if CartItem.objects.filter(products_id = productid, user_id= userid):
                addstock = CartItem.objects.filter(products_id = productid, user_id= userid).aggregate(sum = Sum('quantity', default = 0))
                
                newstock = stock+ addstock.get('sum')
            
                CartItem.objects.filter(products_id = productid, user_id= userid).delete()

                products.objects.filter(id=productid).update(stock=newstock, updateAt = timezone.now())
                
                
                
                return JsonResponse({"msg": "product removed from cart"})

            else:
                return JsonResponse({"msg": "invalid product id"}, status=400)
        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)
    
    
    

def order(request):
    if request.method == 'POST':
        
        totalprice = request.POST.get("totalPrice")
        address = request.POST.get("address")
        user= request.user
        userid = user.id
        
        
        if not totalprice:
            return JsonResponse({"msg": "Total price required"}, status=400)
        if not address:
            return JsonResponse({"msg": "Address required"}, status=400)
        
        
        
        if user.is_authenticated:
            
            Order.objects.create(
                totalPrice = totalprice,
                shippingAddress = address,
                user_id = userid
            )
            
            productid = CartItem.objects.filter(user_id = userid).values("products_id")
            quantity = CartItem.objects.filter(user_id = userid).values("quantity")
            
            print(productid)
            
            
            # for i in productid:
            #     OrderItem.objects.create(
            #         products_id = productid.get("products_id"),
            #         quantity = quantity.get("quantity")
            #     )
            
              # product = products.objects.filter()   

            return JsonResponse({"msg": "Order Placed"}, status=200)
        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)
    


