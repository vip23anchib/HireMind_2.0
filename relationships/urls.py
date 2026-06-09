from django.urls import path
from . import views


from . import views

urlpatterns = [
    

    path(
        'search-candidates-index/',
        views.search_candidates_index,
        name='search_candidates_index'
    )

]

