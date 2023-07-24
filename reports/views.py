from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from accounts.models import *
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser, )
from accounts.serializers import StaffAssessor_Serializer
from performanceManagement.serializers import *
from reports.models import Feedback_sessions
from django.db.models import Q


class CreateEventsAgreements(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["be_evaluated"])
            if check_assessor:
                serializer.save(assessor=request.user)
                serializer.save()
                if (serializer.validated_data['type_report'] == 'E' and not serializer.validated_data[
                    'is_open_agreement']):
                    argument = Events_agreements.objects.get(id=serializer.validated_data['agreement'].id)
                    argument.is_open_agreement = False
                    argument.save()

                return Response(serializer.data)
            else:
                return Response({'msg': request.user.email}, status=400)
        else:
            return Response(serializer.errors, status=400)


class FeedBack(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedBackSerializer

    def post(self, request):
        serializer = FeedBackSerializer(data=request.data)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["be_evaluated"])
            if check_assessor:
                serializer.save(assessor=request.user)
                return Response(serializer.data)
            else:
                return Response({'report': 'you are not assessor of this user'}, status=401)
        else:
            return Response(serializer.errors, status=400)


class ShowAllReportEventsAgreements(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = (StaffAssessor_Serializer, ShowAllReportSerializer)

    def post(self, request):
        serializer = StaffAssessor_Serializer(data=request.data)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["staff"])
            if check_assessor or request.user == serializer.validated_data["staff"]:
                all_data = Events_agreements.objects.filter(
                    assessor=request.user, be_evaluated=serializer.validated_data['staff']).order_by('date_report'
                                                                                                     ).reverse()
                if request.user == serializer.validated_data["staff"]:
                    all_data = Events_agreements.objects.filter(
                        be_evaluated=serializer.validated_data['staff']).order_by('date_report').reverse()
                ser_data = ShowAllReportSerializer(all_data, many=True)
                data = ser_data.data
                for i in range(len(data)):
                    data[i]['indicators_name'] = Indicators.objects.get(id=data[i]['indicators']).name
                    if 'date_report' not in data[i] or not data[i]['date_report']:
                        continue
                    month = data[i]['date_report'].split("-")
                    if len(month) == 0:
                        continue
                    month = int(month[1])
                    season = ""
                    if (month < 4):
                        season = 'B'
                    elif (month < 7):
                        season = 'T'
                    elif (month < 10):
                        season = 'P'
                    else:
                        season = 'Z'
                    data[i]['season_date_report'] = season
                return Response(data)
            else:
                return Response({'report': 'you are not assessor of this user'})
        else:
            return Response(serializer.errors)


class ShowAllAgreementsOpen(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = (StaffAssessor_Serializer, ShowAllReportSerializer)

    def post(self, request):
        serializer = StaffAssessor_Serializer(data=request.data)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["staff"])
            if check_assessor:
                all_data = Events_agreements.objects.filter(assessor=request.user, is_open_agreement=True,
                                                            type_report='A',
                                                            be_evaluated=serializer.validated_data['staff'])
                ser_data = ShowAllReportSerializer(all_data, many=True)
                return Response(ser_data.data)
            else:
                return Response({'report': 'you are not assessor of this user'})
        else:
            return Response(serializer.errors)


class ShowDetailReportEventsAgreements(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return Events_agreements.objects.filter(assessor=self.request.user)


class FeedBackListAssessorAPIView(APIView):
    serializer_class = FeedBackSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StaffAssessor_Serializer(data=request.data)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["staff"])
            if check_assessor:
                query_data = Feedback_sessions.objects.filter(assessor=request.user,
                                                              be_evaluated=serializer.validated_data["staff"]).order_by(
                    'date_report').reverse()
                ser_data = FeedBackSerializer(query_data, many=True).data
                # Has it already been evaluated or not?
                for i in range(len(ser_data)):
                    eval_feedback_session = EvaluationForFeedbackSessions.objects.filter(
                        feedback_session=ser_data[i]['id'])
                    if len(eval_feedback_session) > 0:
                        ser_data[i]['is_eval'] = True
                        ser_data[i]['score'] = eval_feedback_session[0].get_score()

                    else:
                        ser_data[i]['is_eval'] = False
                        ser_data[i]['score'] = 0
                return Response(ser_data)
            else:
                return Response({'report': 'you are not assessor of this user'})
        else:
            return Response(serializer.errors)


class FeddBackSessionListBeEvaluatedAPIView(APIView):
    # queryset = Feedback_sessions.objects.all()
    serializer_class = FeedBackListBeEvalSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self, *args, **kwargs):
    #     return super().get_queryset(*args, **kwargs).filter(be_evaluated=self.request.user).order_by(
    #         'date_report').reverse()
    def get(self, request):
        query_data = Feedback_sessions.objects.filter(be_evaluated=request.user).order_by(
            'date_report').reverse()
        ser_data = FeedBackListBeEvalSerializer(query_data, many=True).data
        # Has it already been evaluated or not?
        for i in range(len(ser_data)):
            eval_feedback_session = EvaluationForFeedbackSessions.objects.filter(
                feedback_session=ser_data[i]['id'])
            if len(eval_feedback_session) > 0:
                ser_data[i]['is_eval'] = True
                ser_data[i]['score'] = eval_feedback_session[0].get_score()

            else:
                ser_data[i]['is_eval'] = False
                ser_data[i]['score'] = 0
        return Response({'results': ser_data})


class FilterObjBaseType(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def post(self, request):
        filtering_data = Events_agreements.objects.filter(type_report="A", assessor=request.user)
        ser_data = EventSerializer(filtering_data, many=True)
        return Response(ser_data.data)


class LikeOrDislike(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeDislikeSerializer

    def post(self, request):
        serializer = LikeDislikeSerializer(data=request.data)
        if serializer.is_valid():
            if Events_agreements.objects.filter(id=request.data['id'], be_evaluated=request.user).count() > 0:
                report = Events_agreements.objects.get(id=request.data['id'], be_evaluated=request.user)
                report.like_dislike = serializer.validated_data['like_dislike']
                report.save()
                return Response({'msg': 'نظر شما ثبت شد'})
            else:
                return Response({'msg': 'شناسه ی ارسالی متعلق به شما نمیباشد.'}, status=403)
        else:
            return Response({'msg': 'اطلاعات ارسالی صحیح نمی باشد'}, status=404)


class ShowQuestionsForFeedbackSessions(ListAPIView):
    queryset = QuestionForFeedbackSessions.objects.all()
    serializer_class = QuestionForFeedbackSessionsSerializer
    permission_classes = [IsAuthenticated]


class EvaluationForFeedbackSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'list_of_eval' not in request.data.keys() or 'feedbackSessionsID' not in request.data.keys():
            return Response(
                {'msg': 'اطلاعات کافی نمیباشد بایستی لیستی از سوالات و همچنین شناسه ی جلسه ی بازخورد را ارسال نمایید.'})

        feedbackSessionsID = request.data['feedbackSessionsID']
        feedbackSessions = Feedback_sessions.objects.filter(id=feedbackSessionsID, be_evaluated=request.user)
        if (feedbackSessions.count() == 0):
            return Response({'msg': 'جلسه ایی متعلق به شما با شناسه ی ارسالی وجود ندارد.'})

        # check Has it already been evaluated or not?
        if len(EvaluationForFeedbackSessions.objects.filter(feedback_session=feedbackSessions[0],
                                                            be_evaluated=request.user)) > 0:
            return Response({'msg': 'شما قبلا این جلسه را ارزیابی نموده اید.'})

        # check if all questions is answered
        list_of_eval = request.data['list_of_eval']
        questions = QuestionForFeedbackSessions.objects.all()
        for q in questions:
            sw = 0
            for eval in list_of_eval:
                if q.id == eval['id'] and eval['score'] < 6 and eval['score'] > 0:
                    sw = 1
                    break
            if sw == 0:
                return Response({
                    'msg': 'شما باید به تمامی سوالات پاسخ دهید و همچنین امتیاز بایستی بین 1 تا 5 باشد. سوال زیر پاسخ داده نشده است\n' + q.questions},
                    status=400)

        # check just all question is exist
        for eval in list_of_eval:
            sw = 0
            for q in questions:
                if q.id == eval['id']:
                    sw = 1
                    break
            if sw == 0:
                return Response({'msg': 'سوال ارسالی در لیست سوالات وجود ندارد' + str(eval['id'])})

        # save the eval
        evaluation_for_feedback_sessions = EvaluationForFeedbackSessions(feedback_session=feedbackSessions[0],
                                                                         be_evaluated=request.user)
        evaluation_for_feedback_sessions.save()
        for eval in list_of_eval:
            question = QuestionForFeedbackSessions.objects.get(id=eval['id'])
            evaluation_question = EvaluationQuestionForFeedbackSessions(question=question, score=eval['score'],
                                                                        description=eval['description'])
            evaluation_question.save()
            evaluation_for_feedback_sessions.questions.add(evaluation_question)
        evaluation_for_feedback_sessions.save()
        return Response({'msg': 'ارزیابی جلسه ی بازخورد با موفقیت ثبت شد'})


class ReportEvaluationForFeedbackSessionsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportEvalForFeedbackSessionsSerializer

    def post(self, request):
        if 'feedbackSessionsID' not in request.data.keys():
            return Response(
                {'msg': 'اطلاعات کافی نمیباشد بایستی شناسه ی جلسه ی بازخورد را ارسال نمایید.'})

        feedbackSessionsID = request.data['feedbackSessionsID']
        feedbackSessions = Feedback_sessions.objects.filter(Q(be_evaluated=request.user) | Q(assessor=request.user),
                                                            id=feedbackSessionsID, )
        if (feedbackSessions.count() == 0):
            return Response({'msg': 'جلسه ایی متعلق به شما با شناسه ی ارسالی وجود ندارد.'})
        evaluation_for_feedback_sessions = EvaluationForFeedbackSessions.objects.filter(
            feedback_session=feedbackSessions[0].id)
        if len(evaluation_for_feedback_sessions) == 0:
            return Response({'msg': 'ارزيابي ايي براي اين جلسه ثبت نشده است'})
        ser_data = ReportEvalForFeedbackSessionsSerializer(evaluation_for_feedback_sessions[0])
        data = ser_data.data
        for i in range(len(data['questions'])):
            q = EvaluationQuestionForFeedbackSessions.objects.get(id=data['questions'][i])
            tmp = {
                'question': q.question.questions,
                'score': q.score,
                'description': q.description
            }
            data['questions'][i] = tmp
        data['score'] = evaluation_for_feedback_sessions[0].get_score()
        return Response(data)


# class ShowAllReportEventsForIndicator(APIView): #dublicate shode ehtemalan bayad ba mohammad check konam
#     permission_classes = [IsAuthenticated]
#     serializer_class = (StaffAssessor_Serializer, ShowAllReportSerializer)
#
#     def post(self, request):
#         serializer = StaffAssessor_Serializer(data=request.data)
#         if serializer.is_valid():
#             check_assessor = staff_assessor.objects.filter(assessor=request.user,
#                                                            staff=serializer.validated_data["staff"])
#             if check_assessor and 'indicator' in request.data.keys():
#                 all_data = Events_agreements.objects.filter(
#                     assessor=request.user, be_evaluated=serializer.validated_data['staff'],
#                     indicators=request.data['indicator']).order_by('date_report').reverse()
#                 ser_data = ShowAllReportSerializer(all_data, many=True)
#                 data = ser_data.data
#                 for i in range(len(data)):
#                     data[i]['indicators_name'] = Indicators.objects.get(id=data[i]['indicators']).name
#                     if 'date_report' not in data[i] or not data[i]['date_report']:
#                         continue
#                     month = data[i]['date_report'].split("-")
#                     if len(month) == 0:
#                         continue
#                     month = int(month[1])
#                     season = ""
#                     if (month < 4):
#                         season = 'B'
#                     elif (month < 7):
#                         season = 'T'
#                     elif (month < 10):
#                         season = 'P'
#                     else:
#                         season = 'Z'
#                     data[i]['season_date_report'] = season
#                 return Response(data)
#             else:
#                 return Response(
#                     {'report': 'یا اطلاعات به صورت کامل ارسال نشده است یا شما ارزیابی کننده این فرد نمیباشید.'})
#         else:
#             return Response(serializer.errors)


class ShowAllEventsAgreementsForIndicator(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = (StaffAssessor_Serializer, ShowAllReportSerializer)

    def post(self, request):
        serializer = StaffAssessor_Serializer(data=request.data)
        if 'indicator' not in request.data.keys():
            return Response({'error': {'msg': 'بايستي شناسه ي شاخص را ارسال نماييد.'}}, status=402)
        if serializer.is_valid():
            check_assessor = staff_assessor.objects.filter(assessor=request.user,
                                                           staff=serializer.validated_data["staff"])
            if check_assessor:
                all_data = Events_agreements.objects.filter(
                    assessor=request.user, be_evaluated=serializer.validated_data['staff'],
                    indicators=request.data['indicator']).order_by('date_report').reverse()
                ser_data = ShowAllReportSerializer(all_data, many=True)
                data = ser_data.data
                for i in range(len(data)):
                    data[i]['indicators_name'] = Indicators.objects.get(id=data[i]['indicators']).name
                    if 'date_report' not in data[i] or not data[i]['date_report']:
                        continue
                    month = data[i]['date_report'].split("-")
                    if len(month) == 0:
                        continue
                    month = int(month[1])
                    season = ""
                    if (month < 4):
                        season = 'B'
                    elif (month < 7):
                        season = 'T'
                    elif (month < 10):
                        season = 'P'
                    else:
                        season = 'Z'
                    data[i]['season_date_report'] = season
                return Response(data)
            else:
                return Response({'report': 'you are not assessor of this user'})
        else:
            return Response(serializer.errors)
