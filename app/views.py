from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import re, json
from .models import products, productImage
from django.utils import timezone
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
        conf_password =request.POST.get("Confirm_password")
        profileImg = request.FILES.get("profileImage")
        
        
        gendervalidate = validate_gender(gender)

        if (
            password
            and email
            and first_name
            and conf_password
            and phoneNo
            and gender
            and profileImg
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
                    profileImage = profileImg,
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
        print(profileImg)
     
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

            # columns = [
            #     "first_name",
            #     "last_name",
            #     "email",
            #     "phone_No",
            #     "date_of_birth",
            #     "gender",
            #     "profileImage",
            # ]

            # data = model_to_dict(user, fields=columns)

            # return JsonResponse(data, status=200)
            return JsonResponse({'image_url' : user.profileImage.url},status=200)
        else:
            return JsonResponse({"msg": "user not login"}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def addproduct(request):
    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        images = request.FILES.getlist("image")

        if request.user.is_authenticated:
            if name and description:
                product = products(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                )
                product.save()

                for image in images:
                    productImage.objects.create(prdoucts=product, image=image)

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
    if request.method == "PUT":
        if not request.body.strip():
            return JsonResponse({"msg": "Enter The User Informations"}, status=400)



        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        images = request.FILES.getlist("image")

        if not validate(name):
            return JsonResponse(
                {"msg": "Title must less then 200 characters"}, status=400
            )

        if not validate_dis(description):
            return JsonResponse({"msg": "Enter Discription"}, status=400)

        if validate_id(updateid):
            return JsonResponse({"msg": "id required"}, status=400)

        if not blogs.objects.filter(id=updateid).exists():
            return JsonResponse({"msg": "id not found"}, status=400)

        current_user = request.user
        cid = current_user.id

        if current_user.is_authenticated:

            if updateid is not None and updateTitle is not None and updatedis is None:
                x = blogs.objects.filter(id=updateid, user_id=cid, active=True).update(
                    title=updateTitle, update=timezone.now()
                )
                if not x:
                    return JsonResponse({"msg": "user is not loged in"}, status=401)
                return JsonResponse({"msg": "Titile Updated successfully"}, status=200)

            if updateid is not None and updatedis is not None and updateTitle is None:
                x = blogs.objects.filter(id=updateid, user_id=cid).update(
                    description=updatedis, update=timezone.now()
                )
                if not x:
                    return JsonResponse({"msg": "user is not loged in"}, status=401)

                return JsonResponse(
                    {"msg": "description Updated successfully"}, status=200
                )

            if (
                updateid is not None
                and updateTitle is not None
                and updatedis is not None
            ):
                x = blogs.objects.filter(id=updateid, user_id=cid).update(
                    title=updateTitle, description=updatedis, update=timezone.now()
                )
                if not x:
                    return JsonResponse({"msg": "user is not loged in"}, status=401)

                return JsonResponse(
                    {"msg": "title and ddescription Updated successfully"}, status=200
                )
            if updateid is not None and updateTitle is None and updatedis is None:

                return JsonResponse(
                    {"msg": "Enter title or description for update"}, status=400
                )

            else:
                return JsonResponse({"msg": "task was not found"}, status=400)

        else:
            return JsonResponse({"msg": "You are not Login"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)
