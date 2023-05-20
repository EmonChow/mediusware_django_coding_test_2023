from django.shortcuts import render,redirect
from commons.pagination import Pagination
from product import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import inlineformset_factory
from product import forms
from django.contrib import messages
from django.db.models import Q


def home_view(request):
    products = models.Product.objects.all()
    product_count = products.count()
    
    variant = models.Variant.objects.all()
    
    # for pagination 
    page = request.GET.get('page')
    size = request.GET.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    products = pagination.paginate_data(products)

    context = {
        'products': products,
        'product_num': product_count,
        'variant': variant
    }
    return render(request, 'home.html',context)




def search_view(request):
    if request.method == 'GET':
        search = request.GET.get('inputTitle') 
        dropdown = request.GET.get('dropdown')
        priceFrom = request.GET.get('from') 
        priceTo = request.GET.get('to')
      
        searchItem = models.Product.objects.all()
        
        if search:
            searchItem = searchItem.filter(title__contains=search)
        if dropdown:
            searchItem = searchItem.filter(productvariant__variant__title=dropdown)
        if priceFrom:
            searchItem = searchItem.filter(productvariantprice__price__gte=int(priceFrom))
        if priceTo:
            searchItem = searchItem.filter(productvariantprice__price__lte=int(priceTo))
        
        context = {
            'products': searchItem,
        }
        return render(request, 'search.html', context)


def add_product_view(request):
    productForm = forms.productForm
    ProductImageForm = forms.ProductImageForm
    ProductFormSet = inlineformset_factory(models.Product, models.ProductVariantPrice,
                                        fk_name='product',
                                        fields=('product_variant_one','product_variant_two','product_variant_three','price','stock'),
                                        extra=2)
    formset = ProductFormSet()
    if request.method=='POST':
        productForm = forms.productForm(request.POST, request.FILES)
        formset = ProductFormSet(request.POST, request.FILES)
        if productForm.is_valid() and formset.is_valid():
            product=productForm.save()
            pd=formset.save(commit=False)
            for p in pd:
                p.product=product
                p.save()
          
            messages.success(request, f"Product has been added")
            return redirect('home')
    context={
        'productForm':productForm,
        'ProductImageForm' : ProductImageForm,
        'formset':formset,
    }
    return render(request, 'product_add.html', context)



def edit_product(request, pk):
   
    product = models.Product.objects.get(id=pk)
    productForm = forms.productForm(instance=product)
    
  
    BookFormSet = inlineformset_factory(models.Product, models.ProductVariantPrice,
                                        fk_name='product',
                                        fields=('product_variant_one','product_variant_two','product_variant_three','price','stock'),
                                        extra=2)
    formset = BookFormSet(instance=product)
    
    if request.method=='POST':
        productForm = forms.productForm( request.POST, request.FILES, instance=product)
        formset = BookFormSet(request.POST, request.FILES, instance=product)
        if productForm.is_valid() and formset.is_valid():
            productForm.save()
            formset.save(commit=False)
            formset.instance=product
            formset.save()
         
            messages.success(request, f"Product has been updated")
            return redirect('home')
    context={
        'productForm':productForm,
        'formset':formset,
        
    }
    return render(request, 'edit_product.html',context)