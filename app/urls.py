from django.urls import path
from app.views import (
    signupview,
    updateUser,
    loginview,
    logoutview,
    addproduct,
    userdetails,
    gender,
    updateProduct,
    deleteProduct,
    productDetails,
    productCategory,
    addtocart,
    removeFromCart,
    filterproduct,
    order,
    cartdata,
    salesInsights,

)


urlpatterns = [
    path("signup/", signupview),
    path("login/", loginview),
    path("updateuser/", updateUser),
    path("logout/", logoutview),
    path("addproduct/", addproduct),
    path("details/", userdetails),
    path("gender/", gender),
    path("updateproduct/", updateProduct),
    path("deleteproduct/", deleteProduct),
    path("productdetails/", productDetails),
    path("productcategory/", productCategory),
    path("addproducts/", productCategory),
    path("addtocart/", addtocart),
    path("removefromcart/", removeFromCart),
    path("filter/", filterproduct),
    path('order/',order),
    path('cartdata/',cartdata),
    path('sales/', salesInsights),
]
