import re
from django.http import JsonResponse
from app.models import User, products, productImage
from django.utils import timezone


def validate_pass(password):

    if password is None:
        return False
    elif re.match(
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%])[A-Za-z\d@$#%]{6,20}$", password
    ):
        return True
    else:
        return False


def validate_username(username):
    if username is None:
        return False
    elif re.match("^[a-z]+$", username):
        return True
    else:
        return False


def validate_email(email):
    if email is None:
        return False

    elif re.match("[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return True
    return False


def FirstName(name):
    if name is None:
        return False
    elif re.match("^[A-Za-z]+$", name):
        return True
    else:
        return False


def LastName(name):
    if name is None or re.match("^[A-Za-z]*$", name):
        return True
    else:
        return False


def validate_phoneNo(no):
    if no is None:
        return False
    elif re.match("^[6-9][0-9]{9}+$", no):
        return True
    else:
        return False


def validate_dob(dob):
    if dob is None:
        return False
    elif re.match(
        "^(((19|20)([2468][048]|[13579][26]|0[48])|2000)[-]02[-]29|((19|20)[0-9]{2}[-](0[4678]|1[02])[-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[-](0[1359]|11)[-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[-](0[1-9]|1[0-9]|2[0-8])))+$",
        dob,
    ):
        return True
    else:
        return False


def validate_gender(gender):
    if gender == "MALE":
        return "Male"
    if gender == "FEMALE":
        return "Female"
    if gender == "OTHER":
        return "Other"
    else:
        return None


def validate_add(add):
    if add is None:
        return False
    else:
        return True


def validate_id(id):
    if id is None or re.match("^\S+$", id):
        return False
    else:
        return True


def convert_gender(gender):
    if gender == "M":
        return "MALE"
    if gender == "F":
        return "FEMALE"
    else:
        return None


def validate(title):
    if title is None or re.match("^\S+$", title) and len(title) >= 200:
        return False
    else:
        return True


def validate_dis(dis):
    if id is None or re.match("^\S+$", dis):
        return False
    else:
        return True





def updateUserDetails(firstName, lastName,  gender, phoneNo, profielimg, userid):
    flag = 0
    if firstName and FirstName(firstName):
        x = User.objects.filter(id=userid).update(first_name=firstName)
        flag = 1
    if lastName and LastName(lastName):
        x = User.objects.filter(id=userid).update(last_name=lastName)
        flag = 1    
    if gender and validate_gender(gender):
        x = User.objects.filter(id=userid).update(gender=gender)
        flag = 1
    if phoneNo and validate_phoneNo(phoneNo):
        x = User.objects.filter(id=userid).update(phone_No=phoneNo)
        flag = 1
    if profielimg:
        x = User.objects.filter(id=userid).update(profileImage=profielimg)
        flag = 1
    if flag == 1:
        return True
    else:
        return False


def updateProductDetails(updateid, name,  description, price, stock, upcategory):
    flag = 0
    if name and validate(name):
        products.objects.filter(id=updateid).update(name=name, updateAt = timezone.now())
        flag = 1
    if description and validate(description):
        products.objects.filter(id=updateid).update(description=description, updateAt = timezone.now())
        flag = 1
    if price:
        products.objects.filter(id=updateid).update(price=price, updateAt = timezone.now())
        flag = 1
    if stock:
        products.objects.filter(id=updateid).update(stock=stock, updateAt = timezone.now())
        flag = 1
    if upcategory:
        products.objects.filter(id=updateid).update(category=upcategory)
        flag = 1
    if flag == 1:
        return True
    else:
        return False