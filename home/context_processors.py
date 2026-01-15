from .models import Store

def active_store_context(request):
    store = None
    store_id = request.session.get('active_store_id')
    if store_id:
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            pass
    return {'active_store': store}
