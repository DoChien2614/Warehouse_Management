from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, ImportReceiptForm, OrderForm, ProductForm, UserUpdateForm, StoreForm, AddEmployeeForm
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib.auth import logout
from .models import Product, ImportReceipt, Order, OrderProduct, Store, StoreUser
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, FloatField
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages



def get_home(request):
    return render(request, 'page1/home.html')

def get_guide(request):
    return render(request, 'page1/guide.html')

def get_product(request):
    return render(request, 'page1/product.html')

def get_contact(request):
    return render(request, 'page1/contact.html')

def get_register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'page1/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('/')

@login_required
def update_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'page1/profile.html', {'form': form})


# ===================== TỒN KHO =====================
@login_required
def inventory_list(request):
    # Chỉ hiển thị inventory theo store hiện tại
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    # Kiểm tra quyền
    if not StoreUser.objects.filter(store=store, user=request.user).exists():
        return HttpResponseForbidden("Bạn không có quyền truy cập cửa hàng này.")

    products = Product.objects.filter(store=store).values(
        'id', 'name', 'category', 'quantity',
        'image', 'purchase_price', 'sale_price',
        'description', 'supplier'
    )
    return JsonResponse(list(products), safe=False)

@login_required
def get_product_tonKho(request):
    category = request.GET.get('category', 'all')
    q = request.GET.get('q', '')
    search_by = request.GET.get('search_by', 'name')
    filter_type = request.GET.get('filter')
    order_by = request.GET.get('order_by', '-date_added')

    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    # Kiểm tra quyền truy cập thông qua StoreUser (không sử dụng user trực tiếp nữa)
    store_user = StoreUser.objects.filter(store=store, user=request.user).first()
    if not store_user:
        return HttpResponseForbidden("Bạn không có quyền truy cập cửa hàng này.")

    # Lọc sản phẩm theo store
    products_list = Product.objects.filter(store=store)
    
    # Lọc theo category nếu có
    if category != 'all':
        products_list = products_list.filter(category=category)

    # Lọc theo từ khóa tìm kiếm (q)
    if q:
        if search_by == 'name':
            products_list = products_list.filter(name__icontains=q)
        elif search_by == 'date_added':
            try:
                date_obj = datetime.strptime(q, '%d/%m/%Y').date()
                products_list = products_list.filter(date_added__date=date_obj)
            except ValueError:
                pass
        elif search_by == 'supplier':
            products_list = products_list.filter(supplier__icontains=q)

    # Lọc theo số lượng tồn kho (nếu cần)
    if filter_type == 'lowstock':
        products_list = products_list.filter(quantity__lte=10)

    # Sắp xếp
    valid_ordering_fields = ['name', '-name', 'date_added', '-date_added']
    if order_by in valid_ordering_fields:
        products_list = products_list.order_by(order_by)

    # Phân trang
    paginator = Paginator(products_list, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # Danh sách các categories
    categories = [
        {'id': 'ao', 'name': 'Áo'},
        {'id': 'quan', 'name': 'Quần'},
        {'id': 'vay', 'name': 'Váy'},
        {'id': 'tat', 'name': 'Tất'},
        {'id': 'giay', 'name': 'Giày'},
        {'id': 'dep', 'name': 'Dép'},
        {'id': 'mu', 'name': 'Mũ'},
        {'id': 'thatlung', 'name': 'Thắt Lưng'},
        {'id': 'khac', 'name': 'Khác'}
    ]

    # Khởi tạo form cho sản phẩm mà không truyền user nữa
    form = ProductForm()  # Không cần user nữa vì quyền đã được kiểm tra qua StoreUser

    # Trả về dữ liệu ra template
    return render(request, 'page1/product-tonkho.html', {
        'products': products,
        'form': form,
        'category': category,
        'categories': categories,
        'order_by': order_by,
        'filter': filter_type,
    })

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Không cần user nữa
        if form.is_valid():
            with transaction.atomic():
                name = form.cleaned_data['name']
                category = form.cleaned_data['category']
                quantity = form.cleaned_data['quantity']

                store_id = request.session.get('active_store_id')
                store = get_object_or_404(Store, id=store_id)

                # Kiểm tra quyền truy cập thông qua StoreUser (không dùng user trực tiếp nữa)
                store_user = StoreUser.objects.filter(store=store, user=request.user).first()
                if not store_user:
                    return HttpResponseForbidden("Bạn không có quyền truy cập cửa hàng này.")

                try:
                    # Cập nhật sản phẩm nếu đã tồn tại
                    product = Product.objects.get(
                        name=name,
                        category=category,
                        store=store
                    )
                    product.description = form.cleaned_data['description']
                    product.sale_price = form.cleaned_data['sale_price']
                    product.purchase_price = form.cleaned_data['purchase_price']
                    product.supplier = form.cleaned_data['supplier']
                    product.quantity += quantity  # Cộng thêm quantity mới vào quantity cũ
                    if form.cleaned_data.get('image'):
                        product.image = form.cleaned_data['image']
                    product.save()
                except Product.DoesNotExist:
                    # Tạo mới sản phẩm nếu chưa tồn tại
                    product = form.save(commit=False)
                    product.store = store
                    product.quantity = quantity  # Gán quantity
                    product.save()

                # Tạo biên lai nhập hàng
                ImportReceipt.objects.create(
                    store=store,
                    name=product.name,
                    category=product.category,
                    quantity=quantity,
                    sale_price=product.purchase_price,
                    supplier=product.supplier
                )

            return redirect('get_product_tonKho')
    else:
        form = ProductForm()  # Không cần user nữa

    return render(request, 'page1/product-tonkho.html', {'form': form})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists() or product.store != store:
        return HttpResponseForbidden("Bạn không có quyền truy cập sản phẩm này.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    form = ProductForm(instance=product)
    return render(request, 'page1/product-tonkho.html', {'form': form, 'product': product})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists() or product.store != store:
        return HttpResponseForbidden("Bạn không có quyền xóa sản phẩm này.")

    product.delete()
    return redirect('get_product_tonKho')


# Chi tiết sản phẩm
def product_detail(request, product_id):
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)
    product = get_object_or_404(Product, id=product_id, store=store)

    if not StoreUser.objects.filter(store=store, user=request.user).exists():
        return HttpResponseForbidden("Bạn không có quyền xem chi tiết sản phẩm này.")

    return render(request, 'page1/product_detail.html', {
        'product': product,
    })


# Phiếu nhập hàng
@login_required
def import_receipt_list(request):
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists():
        return HttpResponseForbidden("Bạn không có quyền truy cập cửa hàng này.")

    receipts = ImportReceipt.objects.filter(store=store).order_by('-date_added')
    return render(request, 'page1/product-phieunh.html', {'receipts': receipts})


def edit_import_receipt(request, receipt_id):
    receipt = get_object_or_404(ImportReceipt, id=receipt_id)
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists() or receipt.store != store:
        return HttpResponseForbidden("Bạn không có quyền chỉnh sửa phiếu này.")

    if request.method == 'POST':
        form = ImportReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            form.save()
        return redirect('import_receipt_list')

    form = ImportReceiptForm(instance=receipt)
    return render(request, 'page1/product-phieunh.html', {'form': form, 'receipt': receipt})


def delete_import_receipt(request, id):
    receipt = get_object_or_404(ImportReceipt, id=id)
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists() or receipt.store != store:
        return HttpResponseForbidden("Bạn không có quyền xóa phiếu này.")

    receipt.delete()
    return redirect('import_receipt_list')


# Thống kê
@login_required
def statistics_view(request):
    user = request.user
    store_id = request.session.get('active_store_id')
    store = get_object_or_404(Store, id=store_id)

    if not StoreUser.objects.filter(store=store, user=request.user).exists():
        return HttpResponseForbidden("Bạn không có quyền xem thống kê của cửa hàng này.")

    current_user_link = StoreUser.objects.get(store_id=store_id, user=request.user)
    if current_user_link.role != 'manager':
        messages.error(request, "Bạn không có quyền thực hiện chức năng này.")
        return redirect('get_home')
    
    # === Nhập hàng ===
    import_receipts = ImportReceipt.objects.filter(store=store)
    import_by_day = import_receipts.annotate(date=TruncDay('date_added')).values('date').annotate(total_quantity=Sum('quantity')).order_by('-date')
    import_by_month = import_receipts.annotate(month=TruncMonth('date_added')).values('month').annotate(total_quantity=Sum('quantity')).order_by('-month')
    import_by_year = import_receipts.annotate(year=TruncYear('date_added')).values('year').annotate(total_quantity=Sum('quantity')).order_by('-year')
    top_suppliers = import_receipts.values('supplier').annotate(name=F('supplier'), total_quantity=Sum('quantity')).order_by('-total_quantity')[:1]
    top_import_categories = import_receipts.values('category').annotate(name=F('category'), total_quantity=Sum('quantity')).order_by('-total_quantity')[:1]

    # === Xuất hàng ===
    orders = Order.objects.filter(store=store)
    order_products = OrderProduct.objects.filter(order__store=store)

    export_by_day = order_products.annotate(date=TruncDay('order__order_date')).values('date').annotate(total_quantity=Sum('quantity')).order_by('-date')
    export_by_month = order_products.annotate(month=TruncMonth('order__order_date')).values('month').annotate(total_quantity=Sum('quantity')).order_by('-month')
    export_by_year = order_products.annotate(year=TruncYear('order__order_date')).values('year').annotate(total_quantity=Sum('quantity')).order_by('-year')
    top_exported_products = order_products.values('product__name').annotate(name=F('product__name'), total_quantity=Sum('quantity')).order_by('-total_quantity')[:1]

    # === Doanh thu ===
    completed_orders = orders.filter(status='completed')
    completed_products = order_products.filter(order__status='completed')

    revenue_by_day = completed_products.annotate(date=TruncDay('order__order_date')).values('date').annotate(
        total_revenue=Sum(F('quantity') * F('product__sale_price'), output_field=FloatField())
    ).order_by('-date')

    revenue_by_month = completed_products.annotate(month=TruncMonth('order__order_date')).values('month').annotate(
        total_revenue=Sum(F('quantity') * F('product__sale_price'), output_field=FloatField())
    ).order_by('-month')

    revenue_by_year = completed_products.annotate(year=TruncYear('order__order_date')).values('year').annotate(
        total_revenue=Sum(F('quantity') * F('product__sale_price'), output_field=FloatField())
    ).order_by('-year')

    revenue_by_category = completed_products.values('product__category').annotate(
        category=F('product__category'),
        total_revenue=Sum(F('quantity') * F('product__sale_price'), output_field=FloatField())
    ).order_by('-total_revenue')

    total_revenue = completed_products.aggregate(
        total=Sum(F('quantity') * F('product__sale_price'), output_field=FloatField())
    )['total'] or 0

    from django.utils.numberformat import format

    def format_currency(amount):
        if amount is None:
            return "0"
        return format(amount, decimal_sep=',', thousand_sep='.', force_grouping=True)

    for item in revenue_by_day:
        item['total_revenue'] = format_currency(item['total_revenue'])
    for item in revenue_by_month:
        item['total_revenue'] = format_currency(item['total_revenue'])
    for item in revenue_by_year:
        item['total_revenue'] = format_currency(item['total_revenue'])
    for item in revenue_by_category:
        item['total_revenue'] = format_currency(item['total_revenue'])

    formatted_total_revenue = format_currency(total_revenue)

    category_display_map = dict(Product.CATEGORY_CHOICES)
    for item in revenue_by_category:
        if item['category'] in category_display_map:
            item['category'] = category_display_map[item['category']]
    for item in top_import_categories:
        if item['name'] in category_display_map:
            item['name'] = category_display_map[item['name']]

    context = {
        'import_by_day': import_by_day,
        'import_by_month': import_by_month,
        'import_by_year': import_by_year,
        'top_suppliers': top_suppliers,
        'top_import_categories': top_import_categories,
        'export_by_day': export_by_day,
        'export_by_month': export_by_month,
        'export_by_year': export_by_year,
        'top_exported_products': top_exported_products,
        'revenue_by_day': revenue_by_day,
        'revenue_by_month': revenue_by_month,
        'revenue_by_year': revenue_by_year,
        'revenue_by_category': revenue_by_category,
        'total_revenue': formatted_total_revenue,
    }
    return render(request, 'page1/product-statistics.html', context)







def parse_order_products(raw_data, request):
    raw_data = raw_data.strip()
    store_id = request.session.get('active_store_id')
    if not store_id:
        return False, "Cửa hàng chưa được chọn"
    
    store = get_object_or_404(Store, id=store_id)

    products_list = []
    for item in raw_data.split(';'):
        if not item.strip():
            continue

        try:
            # Tách "Tên sản phẩm, số lượng" (không còn tên kho)
            product_name, quantity_str = map(str.strip, item.rsplit(',', 1))
            quantity = int(quantity_str)
            if quantity <= 0:
                return False, 'Số lượng phải lớn hơn 0'

            # Lấy product theo store
            product = Product.objects.get(name=product_name, store=store)

            # Kiểm tra tồn kho
            if product.quantity < quantity:
                return False, (
                    f"Sản phẩm '{product.name}' không đủ hàng "
                    f"(còn {product.quantity})"
                )

            products_list.append((product, quantity)) # Chỉ lưu product và quantity

        except ValueError:
            return False, (
                "Sai định dạng. Định dạng đúng là: "
                "'Tên sản phẩm, số lượng;'" # Cập nhật thông báo lỗi
            )
        except Product.DoesNotExist:
            return False, f"Sản phẩm '{product_name}' không tồn tại trong cửa hàng"

    if not products_list:
        return False, 'Không có sản phẩm hợp lệ trong đơn hàng'

    return True, products_list

@login_required
def get_order(request):
    store = get_object_or_404(Store, id=request.session.get('active_store_id'))

    orders_list = Order.objects.filter(store=store).order_by('-order_date')
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    form = OrderForm(request.POST or None)
    # form.store_user = store_user  # No longer needed

    return render(request, 'page1/order.html', {'orders': orders, 'form': form})

@login_required
def add_order(request):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=request.session.get('active_store_id'))
        
        # Lấy StoreUser
        store_user = get_object_or_404(StoreUser, user=request.user, store=store)
        
        form = OrderForm(request.POST)
        if form.is_valid():
            raw_order_data = form.cleaned_data['order_products']
            success, result = parse_order_products(raw_order_data, request)

            if not success:
                return JsonResponse({'status': 'error', 'message': result})

            order_code = form.cleaned_data['order_code']
            if Order.objects.filter(store_user=store_user, store=store, order_code=order_code).exists():
                return JsonResponse({'status': 'error', 'message': 'Mã đơn hàng đã tồn tại!'})

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.store_user = store_user
                    order.store = store
                    order.status = 'shipping'
                    order.save()

                    for product, quantity in result: # Thay đổi ở đây
                        #inventory = ProductInventory.objects.select_for_update().get(product=product, warehouse=warehouse)
                        if product.quantity < quantity: # Kiểm tra trực tiếp trên product
                            raise ValueError(f"Sản phẩm '{product.name}' không đủ hàng")
                        product.quantity -= quantity # Cập nhật trực tiếp trên product
                        product.save()

                        OrderProduct.objects.create(order=order, product=product, quantity=quantity) # Bỏ warehouse

                    return JsonResponse({"status": "success"})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        else:
            return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ'})

    return JsonResponse({'status': 'error', 'message': 'Phương thức không phải POST'})

@login_required
def delete_order(request, order_id):
    try:
        store = get_object_or_404(Store, id=request.session.get('active_store_id'))
        with transaction.atomic():
            order = Order.objects.get(id=order_id, store_user__user=request.user, store=store)
            for op in OrderProduct.objects.filter(order=order):
                #inventory = ProductInventory.objects.select_for_update().get(product=op.product, warehouse=op.warehouse)
                product = Product.objects.select_for_update().get(id=op.product.id) # Lấy product để cập nhật
                product.quantity += op.quantity # Trả lại số lượng
                product.save()
            order.delete()
        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def update_order_status(request, order_id):
    try:
        store = get_object_or_404(Store, id=request.session.get('active_store_id'))
        with transaction.atomic():
            # Sửa truy vấn để sử dụng store_user__user thay vì user
            order = Order.objects.get(id=order_id, store=store, store_user__user=request.user)
            old_status = order.status
            new_status = request.POST.get('status')

            if new_status not in ['shipping', 'completed', 'canceled', 'returned']:
                return JsonResponse({'status': 'error', 'message': 'Trạng thái không hợp lệ'})

            for op in OrderProduct.objects.filter(order=order):
                #inventory = ProductInventory.objects.select_for_update().get(product=op.product, warehouse=op.warehouse)
                product = Product.objects.select_for_update().get(id=op.product.id) # Lấy product để cập nhật
                if old_status == 'shipping' and new_status == 'canceled':
                    product.quantity += op.quantity # Trả lại số lượng
                elif old_status == 'canceled' and new_status == 'shipping':
                    if product.quantity < op.quantity: # Kiểm tra trực tiếp trên product
                        return JsonResponse({'status': 'error', 'message': f'Sản phẩm {op.product.name} không đủ hàng'})
                    product.quantity -= op.quantity # Lấy đi số lượng
                elif old_status == 'completed' and new_status == 'returned':
                    product.quantity += op.quantity # Trả lại số lượng
                product.save()

            order.status = new_status
            order.save()
        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy đơn hàng'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@login_required
def view_order(request, order_id):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')  # nếu không có cửa hàng, chuyển hướng

    order = get_object_or_404(
        Order, 
        id=order_id, 
        store=Store.objects.get(id=store_id),
        store_user__user=request.user  # Lọc theo user của store_user
    )
    return render(request, 'page1/order-details.html', {'order': order})

from django.utils.dateparse import parse_date

@login_required
def search_orders(request):
    store = get_object_or_404(Store, id=request.session.get('active_store_id'))
    
    # Lấy StoreUser
    store_user = get_object_or_404(StoreUser, user=request.user, store=store)

    query = request.GET.get('q', '').strip().lower()
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    orders = Order.objects.filter(store_user=store_user, store=store).distinct()

    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if start_date and end_date:
            orders = orders.filter(order_date__range=(start_date, end_date))

    if query:
        orders = orders.filter(
            Q(order_code__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_phone__icontains=query) |
            Q(customer_address__icontains=query) |
            Q(shipping_unit__icontains=query) |
            Q(order_products__product__name__icontains=query)
        ).distinct()

    if not query and not (start_date_str and end_date_str):
        return JsonResponse({'status': 'error', 'message': 'Bạn chưa nhập nội dung tìm kiếm.'})

    page_number = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page_number)

    results = [
        {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'order_date': order.order_date.isoformat(),
            'status': order.status,
            'shipping_unit': order.shipping_unit
        }
        for order in page_obj
    ]

    pagination_html = render_to_string(
        'page1/pagination_fragment.html',
        {
            'orders': page_obj,
            'currentStatus': None,
            'query': query,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }
    )
    return JsonResponse({'status': 'success', 'orders': results, 'pagination_html': pagination_html})

@login_required
def filter_orders(request):
    store = get_object_or_404(Store, id=request.session.get('active_store_id'))
    status = request.GET.get('status', '')
    page = request.GET.get('page', 1)

    # Lấy StoreUser
    store_user = get_object_or_404(StoreUser, user=request.user, store=store)

    orders = Order.objects.filter(store_user=store_user, store=store)
    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page)

    orders_data = [
        {
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'shipping_unit': order.shipping_unit,
            'status': order.status,
            'id': order.id
        }
        for order in page_obj
    ]

    pagination_html = render_to_string('page1/pagination_fragment.html', {'orders': page_obj})

    return JsonResponse({
        'status': 'success',
        'orders': orders_data,
        'pagination_html': pagination_html
    })

#store
from .models import Store
from .forms import StoreForm  # form tạo store nếu cần

@login_required
def select_store(request):
    store_links = StoreUser.objects.filter(user=request.user)
    stores = [link.store for link in store_links]

    if request.method == 'POST':
        store_id = request.POST.get('store_id')
        if any(s.id == int(store_id) for s in stores):
            request.session['active_store_id'] = store_id
            return redirect('/')
    
    return render(request, 'page1/select_store.html', {'stores': stores})

@login_required
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            StoreUser.objects.create(user=request.user, store=store, role='manager')
            request.session['active_store_id'] = store.id
            return redirect('/')
    else:
        form = StoreForm()
    return render(request, 'page1/create_store.html', {'form': form})

@login_required
def store_info(request):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')  # nếu chưa chọn cửa hàng thì chuyển đến trang chọn

    try:
        store_user = StoreUser.objects.filter(user=request.user, store_id=store_id).first()
        if not store_user:
            return redirect('select_store')  # Nếu không tìm thấy cửa hàng cho người dùng này
        store = store_user.store  # Lấy cửa hàng từ StoreUser
    except StoreUser.DoesNotExist:
        return redirect('select_store')

    # Kiểm tra xem người dùng có phải là manager không
    is_manager = store_user.role == 'manager'
    is_staff = store_user.role == 'staff'

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect(request.path)
    else:
        form = StoreForm(instance=store)

    return render(request, 'page1/store_info.html', {
        'form': form,
        'store': store,
        'is_manager': is_manager,
        'is_staff': is_staff
    })

@login_required
def delete_store(request):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')

    try:
        store_user = StoreUser.objects.filter(user=request.user, store_id=store_id).first()
        if not store_user:
            return redirect('select_store')  # Nếu không tìm thấy cửa hàng cho người dùng này
        store = store_user.store

    except Store.DoesNotExist:
        return redirect('select_store')

    if request.method == 'POST':
        store.delete()
        request.session['active_store_id'] = None
        return redirect('select_store')
    
@login_required
def add_employee(request):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')  # Chuyển đến trang chọn cửa hàng nếu chưa có cửa hàng hoạt động

    try:
        store = Store.objects.get(id=store_id)
        link = StoreUser.objects.get(store=store, user=request.user)
        if link.role != 'manager':
            return HttpResponseForbidden("Bạn không có quyền thêm nhân viên")  # Chỉ người có quyền quản lý mới có thể thêm nhân viên
    except Store.DoesNotExist:
        return redirect('select_store')

    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            try:
                user = User.objects.get(username=username)
                StoreUser.objects.create(user=user, store=store, role=role)  # Thêm nhân viên vào cửa hàng
                return redirect('store_info')  # Sau khi thêm nhân viên, quay lại trang thông tin cửa hàng
            except User.DoesNotExist:
                form.add_error('username', 'Không tìm thấy người dùng')  # Thông báo nếu không tìm thấy người dùng
    else:
        form = AddEmployeeForm()

    return render(request, 'page1/add_employee.html', {'form': form})

@login_required
def remove_employee(request, user_id):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')

    try:
        store_user = StoreUser.objects.get(store_id=store_id, user=request.user)
        if store_user.role != 'manager':
            return HttpResponseForbidden("Bạn không có quyền")
    except StoreUser.DoesNotExist:
        return redirect('select_store')

    # Không cho tự xóa chính mình
    if user_id == request.user.id:
        return HttpResponseForbidden("Không thể tự xóa chính mình")

    try:
        target_link = StoreUser.objects.get(store_id=store_id, user_id=user_id)
        target_link.delete()
    except StoreUser.DoesNotExist:
        pass

    return redirect('store_info')

from django import forms

class EditEmployeeRoleForm(forms.Form):
    role = forms.ChoiceField(choices=[
        ('manager', 'Quản lý'),
        ('staff', 'Nhân viên')
    ])

@login_required
def edit_employee_role(request, user_id):
    store_id = request.session.get('active_store_id')
    if not store_id:
        return redirect('select_store')

    try:
        current_user_link = StoreUser.objects.get(store_id=store_id, user=request.user)
        if current_user_link.role != 'manager':
            return HttpResponseForbidden("Bạn không có quyền")
    except StoreUser.DoesNotExist:
        return redirect('select_store')

    try:
        target_link = StoreUser.objects.get(store_id=store_id, user_id=user_id)
    except StoreUser.DoesNotExist:
        return HttpResponseForbidden("Nhân viên không tồn tại trong cửa hàng")

    # Prevent editing own role
    if target_link.user.id == request.user.id:
        return HttpResponseForbidden("Bạn không thể tự sửa quyền của mình.")

    if request.method == 'POST':
        form = EditEmployeeRoleForm(request.POST)
        if form.is_valid():
            target_link.role = form.cleaned_data['role']
            target_link.save()
            return redirect('store_info')
    else:
        form = EditEmployeeRoleForm(initial={'role': target_link.role})

    return render(request, 'page1/edit_employee.html', {'form': form, 'employee': target_link.user})

