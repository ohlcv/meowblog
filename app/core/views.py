from django.shortcuts import render

def homepage(request):
    return render(request, 'core/homepage.html')

def about(request):
    """关于我页面"""
    return render(request, 'core/about.html')

def terms_of_service(request):
    """服务协议页面"""
    return render(request, 'core/terms_of_service.html')

def privacy_policy(request):
    """隐私政策页面"""
    return render(request, 'core/privacy_policy.html')

def disclaimer(request):
    """免责声明页面"""
    return render(request, 'core/disclaimer.html')