from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import staff_assessor
from accounts.serializers import StaffAssessor_Serializer
from performanceManagement.serializers import *
from accounts.views import get_season_isEvalTime
from rest_framework.views import APIView
from persiantools.jdatetime import JalaliDate
from django.db.models import Q


class IndicatorsListAPIView(ListAPIView):
    queryset = Indicators.objects.all()
    serializer_class = IndicatorsListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(assessor=self.request.user) | Q(assessor__isnull=True))


class ItemsEvaluationList(ListAPIView):
    queryset = Items_evaluation.objects.all()
    serializer_class = ItemsEvaluationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class AxesList(ListAPIView):
    queryset = Axes.objects.all()
    serializer_class = AxesListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class getIndicatorsForAccount(APIView):
    serializer_class = (StaffAssessor_Serializer, EvaluationListSerializer)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer_request = StaffAssessor_Serializer(data=request.data)
        if serializer_request.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer_request.validated_data["staff"])
            if check_assessor:
                all_data_staff = Indicators.objects.filter(be_evaluated=serializer_request.validated_data["staff"],
                                                           assessor=request.user)
                all_data_public = Indicators.objects.filter(assessor__isnull=True).order_by()
                serializer_data_staff = EvaluationListSerializer(all_data_staff, many=True)
                serializer_data_public = EvaluationListSerializer(all_data_public, many=True)
                data = serializer_data_public.data + serializer_data_staff.data
                check_not_duplicate = []
                result_data = []
                for i in range(len(data)):
                    if data[i]['id'] in check_not_duplicate:
                        continue
                    check_not_duplicate.append(data[i]['id'])
                    data[i]['item_of_indicators'] = Indicators.objects.get(
                        id=data[i]['id']).items.values_list().order_by('score')
                    data[i]['axes_name'] = Axes.objects.get(id=data[i]['axes']).name
                    del data[i]["items"]
                    del data[i]["assessor"]
                    del data[i]["be_evaluated"]
                    result_data.append(data[i])

                return Response(result_data)
            else:
                return Response({'msg': "you are not assessor of this user"}, status=401)
        else:
            return Response({'msg': serializer_request.errors}, status=401)


class EvalAccaount(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # check is eval time
        if not get_season_isEvalTime()['is_eval_time']:
            return Response({'msg': 'هم اکنون زمان ارزیابی نمی باشد.'}, status=400)
        # check information is sent
        if not 'list_of_eval' in request.data.keys() or not 'staff' in request.data.keys():
            return Response({'msg': 'اطلاعات کامل نمیباشد لطفاً نام ارزیابی شونده و لیست امتیازها را ارسال نمایید.'},
                            status=400)
        staff = Account.objects.filter(id=request.data['staff'])
        if len(staff) == 0:
            return Response({'msg': 'چنین کاربری وجود ندارد.'}, status=400)
        staff = staff[0]
        check_assessor = staff_assessor.objects.filter(assessor=request.user, staff=staff)
        # check user is assessor of him/her
        if len(check_assessor) == 0:
            return Response({'msg': "شما ارزیاب این ارزیابی شونده نیستید."}, status=400)
        list_of_eval = request.data['list_of_eval']
        # check list of eval is correct
        for eval in list_of_eval:
            if len(Indicators.objects.filter(id=eval[0])) == 0 or len(Items_evaluation.objects.filter(id=eval[1])) == 0:
                return Response({'msg': 'لیست امتیازها صحصح نمیباشد ' + str(eval)})
        current_year = JalaliDate.today().year
        # check zemestan
        year_report = current_year if get_season_isEvalTime()['season_eval'] != 'Z' else current_year - 1

        check_if_exist_report = Eval_Report.objects.filter(assessor=request.user, be_evaluated=staff,
                                                           season=get_season_isEvalTime()['season_eval'],
                                                           year=year_report)
        # if exit must be delete
        if len(check_if_exist_report) > 0:
            check_if_exist_report[0].delete()
        # create report
        report = Eval_Report(assessor=request.user,
                             be_evaluated=staff,
                             season=get_season_isEvalTime()['season_eval'],
                             year=year_report)
        report.save()
        # get indicators of staff
        all_data_staff = Indicators.objects.filter(
            Q(be_evaluated=staff, assessor=request.user) | Q(assessor__isnull=True))
        serializer_data_staff = EvaluationListSerializer(all_data_staff, many=True).data
        for i in range(len(list_of_eval)):
            for j in range(len(serializer_data_staff)):
                if list_of_eval[i][0] == serializer_data_staff[j]['id']:
                    indicators = Indicators.objects.get(id=list_of_eval[i][0])
                    items_evaluation = Items_evaluation.objects.get(id=list_of_eval[i][1])
                    evaluation_new = Evaluation(indicators=indicators, items_evaluation=items_evaluation)
                    evaluation_new.save()
                    report.evaluations.add(evaluation_new)
                    break

        report.save()

        # report
        report = Eval_Report.objects.filter(assessor=request.user,
                                            be_evaluated=staff,
                                            season=get_season_isEvalTime()['season_eval'],
                                            year=JalaliDate.today().year)
        serializer_data = ReportEvalSerializer(report, many=True)
        return Response({'result': serializer_data.data, 'msg': 'success'})


class getReportEval(APIView):
    serializer_class = (StaffAssessor_Serializer, EvaluationListSerializer)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer_request = StaffAssessor_Serializer(data=request.data)
        if serializer_request.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer_request.validated_data["staff"])
            season = request.data['season']
            year = request.data['year']
            if (check_assessor and season and year) or request.user == serializer_request.validated_data["staff"]:
                report = Eval_Report.objects.filter(assessor=request.user, season=season, year=year,
                                                    be_evaluated=serializer_request.validated_data["staff"])
                # user wants to see your own report
                if request.user == serializer_request.validated_data["staff"]:
                    report = Eval_Report.objects.filter(be_evaluated=serializer_request.validated_data["staff"],
                                                        season=season, year=year, display=True)
                if len(report) == 0:
                    return Response([])
                serializer_data = ReportEvalSerializer(report, many=True)
                data = serializer_data.data
                for i in range(len(data)):
                    tmp = []
                    score = Eval_Report.objects.get(id=data[i]['id']).get_score()
                    for j in range(len(data[i]['evaluations'])):
                        ev_obg = Evaluation.objects.get(id=data[i]['evaluations'][j])
                        tmp.append([ev_obg.indicators.name, ev_obg.items_evaluation.name])
                    data[i]['report'] = tmp
                    data[i]['score'] = score
                    del data[i]['evaluations']
                return Response(data)
            else:
                return Response({'msg': "you are not assessor of this user or dose not sent year or season"},
                                status=403)
        else:
            return Response({'msg': serializer_request.errors}, status=401)
