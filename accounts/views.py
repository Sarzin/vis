from rest_framework.generics import UpdateAPIView

from accounts.forms import chaneg_pass_Form
from reports.serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from persiantools.jdatetime import JalaliDate


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class PostCreateAPIViewAccount(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = PostCreateSerializerAccount


class PostListAPIViewAccount(generics.ListAPIView):
    # queryset = Article.objects.all()
    serializer_class = PostListSerializerAccount
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self, *args, **kwargs):
        return Account.objects.filter(be_evaluated__assessor__username=self.request.user.username)


def logout_view(request):
    logout(request)
    return redirect('/')


class AddEvaluatedUser(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateEvaluatedUser

    def post(self, request):
        serializer = CreateEvaluatedUser(data=request.data)
        if serializer.is_valid():
            check_user = Account.objects.filter(email=serializer.validated_data["email"])
            if not check_user.exists():
                Account.objects.create_user(first_name=serializer.validated_data["first_name"],
                                            last_name=serializer.validated_data["last_name"],
                                            username=serializer.validated_data["username"],
                                            email=serializer.validated_data["email"],
                                            job_side=serializer.validated_data["job_side"]
                                            )

                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        else:
            return Response(serializer.errors)


class AddUnit(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddNewUnit

    def post(self, request):
        serializer = AddNewUnit(data=request.data)
        if serializer.is_valid():
            unit = Unit.objects.filter(name=serializer.validated_data["name"])
            if not unit.exists():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        else:
            return Response(serializer.errors)


class GetOneEvaluatedUser(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostListSerializerAccount

    def get(self, request):
        try:
            data = Account.objects.get(pk=request.user.id)
            ser_data = PostListSerializerAccount(data)
        except Account.DoesNotExist:
            return Response({'Error': "This user does not exists"})
        return Response(ser_data.data)


class ShowEventOrAgreementsForEvaluatedUser(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShowAllReportSerializer

    def post(self, request):
        if request.data["type_report"] == 'A' or request.data["type_report"] == 'E':
            queryset_data = Events_agreements.objects.filter(type_report=request.data["type_report"],
                                                             be_evaluated=request.user
                                                             ).order_by('date_report').reverse()
            ser_data = ShowAllReportSerializer(queryset_data, many=True).data
            # be_seen have to be True
            for event in queryset_data:
                event.be_seen = True
                event.save()
            return Response(ser_data)
        else:
            return Response({'msg': 'لطفاً نوع گزارش را مشخص نمایید.'}, status=404)


def get_season_isEvalTime():
    if (JalaliDate.today().month < 4):
        season = 'B'
        season_eval = 'Z'
    elif (JalaliDate.today().month < 7):
        season = 'T'
        season_eval = 'B'
    elif (JalaliDate.today().month < 10):
        season = 'P'
        season_eval = 'T'
    else:
        season = 'Z'
        season_eval = 'P'

    if ((JalaliDate.today().month == 4 or JalaliDate.today().month == 7 or
         JalaliDate.today().month == 10 or JalaliDate.today().month == 1) and
            JalaliDate.today().day < 10):
        is_eval_time = True
    else:
        is_eval_time = False

    report = {
        'season': season,
        'season_eval': season_eval,
        'is_eval_time': is_eval_time,
        'year': JalaliDate.today().year
    }
    return report


class UnitList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.assessor:
            return Response({'msg': 'you are not assessor'}, status=400)
        query = staff_assessor.objects.filter(assessor=request.user)
        list_unit = []

        # for check new unit is in list or not
        just_unit_tmp = []

        for account in query:
            if account.staff.unit:
                if account.staff.unit.name not in just_unit_tmp:
                    list_unit.append([account.staff.unit.name, account.staff.unit.id])
                    just_unit_tmp.append(account.staff.unit.name)

        return Response({'unit': list_unit})


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = Account
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def change_user_pass(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if request.user.admin == False:
        return redirect("/")

    if request.method != 'POST':
        form = chaneg_pass_Form()
        return render(request, 'accounts/change_pass.html', {'form': form})
    else:
        form = chaneg_pass_Form(request.POST)
        username = form.data["username"]
        password = form.data["password"]
        try:
            account_to_change = Account.objects.get(username=username)
        except:
            account_to_change = None
        if account_to_change != None:
            account_to_change.set_password(password)
            account_to_change.save()
            return render(request, 'accounts/change_pass.html', {'sucess': 'گذرواژه تغییر گردید', 'form': form})
        else:
            return render(request, 'accounts/change_pass.html', {'error': 'کاربر پیدا نشد', 'form': form})

# from scripts.add_unit_to_data_base import script
# from scripts.accounts_scripts_csv_to_database import script
# from scripts.staff_assesor_scripts_csv_to_database import script
# from scripts.add_feed_back_session import script
# from scripts.add_indicators import script
# from scripts.add_event_to_database import script
# from scripts.list_users_dose_not_change_pass import script
# from threading import Thread
#
#
# class runscript(APIView):
#     def post(self, request):
#         t1 = Thread(target=script.get_list_of_user, args=(script,))
#         t1.start()
#         return Response({"msg": "script run shod"})
