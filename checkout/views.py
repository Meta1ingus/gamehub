from django.shortcuts import render

def success(request):
    return render(request, "checkout/success.html")

def cancel(request):
    return render(request, "checkout/cancel.html")
