from django.urls import path
from accounts.views import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls import url

app_name = 'accounts'

urlpatterns = [
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'create', PostCreateAPIViewAccount.as_view(), name='create'),
    url(r'^users', PostListAPIViewAccount.as_view(), name='users'),
    path("add-new-evaluated-user/", AddEvaluatedUser.as_view(), name="add_evaluated_user"),
    path("add-new-unit/", AddUnit.as_view(), name="add_new_unit"),
    path("one-evaluated-user/", GetOneEvaluatedUser.as_view(), name="one_evaluated_user"),
    path("listUnit/", UnitList.as_view(), name="List-of-unit"),
    path("show-event-for-evaluated-user/", ShowEventOrAgreementsForEvaluatedUser.as_view(),
         name="event_for_evaluated_user"),
    # path("run-scripts/", runscript.as_view(), name="runscript"),
    path("change_user_pass", change_user_pass, name="change_user_pass"),
    path('change_password/', ChangePasswordView.as_view(), name='auth_change_password'),

]
