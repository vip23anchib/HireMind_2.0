# We use relative imports (from .filename) to bring the views to the front desk
from .main_views import (
    
    success_view,
    login_view,
    logout_view,
    form_data,
    form_submit,
    ajax_data,
    edit_data,
    delete_data,
    search_candidates,
    candidate_profile,
    ats_dashboard,

)

from .form_views import(
    form
)