from rest_framework.views import APIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser, )
from rest_framework.response import Response
from persiantools.jdatetime import JalaliDate
from reports.models import Events_agreements, Eval_Report, Feedback_sessions, EvaluationForFeedbackSessions
from accounts.models import staff_assessor
from django.db.models import Q
from accounts.views import get_season_isEvalTime


class AssessorData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        num_be_eval = len(staff_assessor.objects.filter(assessor=request.user))
        num_argument = len(Events_agreements.objects.filter(type_report='A', assessor=request.user))
        num_event = len(Events_agreements.objects.filter(type_report='E', assessor=request.user))
        ave_argument = 0 if num_be_eval == 0 else num_argument / num_be_eval
        num_open_argument = len(
            Events_agreements.objects.filter(type_report='A', assessor=request.user, is_open_agreement=True))
        num_feedback_session = len(Feedback_sessions.objects.filter(assessor=request.user))
        data = {
            'num_be_eval': num_be_eval,
            'num_argument': num_argument,
            'num_event': num_event,
            'ave_argument': round(ave_argument, 1),
            'num_open_argument': num_open_argument,
            'personnel_code': request.user.Personnel_Code,
            'unit': '' if request.user.unit == None else request.user.unit.name,
            'num_feedback_session': num_feedback_session
        }
        return Response({'data': data})


class AssessorEventArgumentCharts(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chart_argument = self.event_argument_chart(request, 'A')
        chart_event = self.event_argument_chart(request, 'E')
        data = {
            'num_argument': chart_argument,
            'num_event': chart_event
        }
        return Response(data=data)

    def convert_num_to_month(self, month):
        if month == 1: return 'فروردین'
        if month == 2: return 'اردیبهشت'
        if month == 3: return 'خرداد'
        if month == 4: return 'تیر'
        if month == 5: return 'مرداد'
        if month == 6: return 'شهریور'
        if month == 7: return 'مهر'
        if month == 8: return 'آبان'
        if month == 9: return 'آذر'
        if month == 10: return 'دی'
        if month == 11: return 'بهمن'
        if month == 12: return 'اسفند'

    def event_argument_chart(self, request, type):
        chart_argument = []
        tmp = 0
        # shwo last 3 manth
        for i in range(3):
            year = JalaliDate.today().year
            month = JalaliDate.today().month - i

            # If it is the first month of the year, the previous month will be the last month of the year
            if month < 1:
                month = month + 12
            # convert to Miladi
            this_month = JalaliDate(year, month, 1).to_gregorian()
            num_this_month = len(Events_agreements.objects.filter(date_report__gte=this_month, assessor=request.user,
                                                                  type_report=type)) - tmp
            chart_argument.append({'name': self.convert_num_to_month(month), 'value': num_this_month})
            tmp = num_this_month + tmp
        return chart_argument


class AssessorAverageEvalFBeginning(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        year = JalaliDate.today().year
        average_eval = []

        # set defult score
        min_score = {'score': 100, 'be_eval': ''}
        max_score = {'score': 0, 'be_eval': ''}

        # The loop continues until we reach a year that has no evaluation.
        while (True):
            evals = Eval_Report.objects.filter(assessor=request.user, year=year)
            if year == 1400:
                break
            sum = 0
            # Summing up all the evaluations of that year And check min and max
            for eval in evals:
                score = eval.get_score()
                sum = sum + score
                if (score > max_score['score']):
                    max_score['score'] = score
                    max_score['be_eval'] = eval
                if (score < min_score['score']):
                    min_score['score'] = score
                    min_score['be_eval'] = eval
            average = 0 if len(evals) == 0 else sum / len(evals)
            average_eval.append({'year': year, 'average': round(average, 1)})
            year = year - 1

        return Response({'data':
            {
                'min': {
                    'name': min_score['be_eval'].be_evaluated.get_full_name(),
                    'score': min_score['be_eval'].get_score()
                },
                'max': {
                    'name': max_score['be_eval'].be_evaluated.get_full_name(),
                    'score': max_score['be_eval'].get_score()
                },
                'average_eval': average_eval
            }
        })


class AssessorAverageEvalCurrent(APIView):
    permission_classes = [IsAuthenticated]

    def get_ave_min_max(self, evals):
        # if it was empty
        if len(evals) == 0:
            return {
                'average': 0,
                'min_score': {'score': 100, 'be_eval': 'nobody'},
                'max_score': {'score': 0, 'be_eval': 'nobody'}
            }

        sum = 0

        # Defult min and max score
        min_score = {'score': 100, 'be_eval': ''}
        max_score = {'score': 0, 'be_eval': ''}
        # Summing up all the evaluations of that evals And check min and max
        for eval in evals:
            score = eval.get_score()
            sum = sum + score
            if (score > max_score['score']):
                max_score['score'] = score
                max_score['be_eval'] = eval.be_evaluated.get_full_name(),
            if (score < min_score['score']):
                min_score['score'] = score
                min_score['be_eval'] = eval.be_evaluated.get_full_name(),
        average = 0 if len(evals) == 0 else sum / len(evals)
        data = {
            'average': round(average, 1),
            'min_score': min_score,
            'max_score': max_score
        }
        return data

    def post(self, request):
        year = JalaliDate.today().year
        data = {
            'bahar': self.get_ave_min_max(Eval_Report.objects.filter(assessor=request.user, year=year, season='B')),
            'tabestan': self.get_ave_min_max(Eval_Report.objects.filter(assessor=request.user, year=year, season='T')),
            'paeez': self.get_ave_min_max(Eval_Report.objects.filter(assessor=request.user, year=year, season='P')),
            'zemestan': self.get_ave_min_max(Eval_Report.objects.filter(assessor=request.user, year=year, season='Z')),
        }

        # Setting the first chapter as total min and max
        total_min = {'score': data['bahar']['min_score']['score'], 'be_eval': data['bahar']['min_score']['be_eval']}
        total_max = {'score': data['bahar']['max_score']['score'], 'be_eval': data['bahar']['max_score']['be_eval']}

        # check min and max
        for key in data:
            if data[key]['max_score']['score'] > total_max['score']:
                total_max['score'] = data[key]['max_score']['score']
                total_max['be_eval'] = data[key]['max_score']['be_eval']
            if data[key]['min_score']['score'] < total_min['score']:
                total_min['score'] = data[key]['min_score']['score']
                total_min['be_eval'] = data[key]['min_score']['be_eval']

        data['min_score'] = total_min
        data['max_score'] = total_max

        return Response({
            'data': data
        })


class AssessorUserReportTable(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        num_agreements = len(Events_agreements.objects.filter(assessor=request.user, type_report='A'))
        num_event = len(Events_agreements.objects.filter(assessor=request.user, type_report='E'))
        num_be_eval = len(staff_assessor.objects.filter(assessor=request.user))

        # Compute average of Evaluvation
        evals = Eval_Report.objects.filter(assessor=request.user)
        ave_evals = 0
        for eval in evals:
            ave_evals = ave_evals + eval.get_score()
        ave_evals = 0 if len(evals) == 0 else ave_evals / len(evals)

        num_feedback_session = len(Feedback_sessions.objects.filter(assessor=request.user))
        be_evals = staff_assessor.objects.filter(assessor=request.user)
        ave_feedback_session = 0
        num_feedback_session = 0
        for person in be_evals:
            evals = EvaluationForFeedbackSessions.objects.filter(be_evaluated=person.staff)
            for eval in evals:
                ave_feedback_session = ave_feedback_session + eval.get_score()
                num_feedback_session += 1
        ave_feedback_session = 0 if num_feedback_session == 0 else ave_feedback_session / num_feedback_session
        season_info = get_season_isEvalTime()
        data = {
            'name': request.user.get_full_name(),
            'personal_code': request.user.Personnel_Code,
            'unit': '' if request.user.unit == None else request.user.unit.name,
            'season': season_info['season'],
            'year': season_info['year'],
            'num_agreements': num_agreements,
            'num_event': num_event,
            'num_be_eval': num_be_eval,
            'ave_eval': round(ave_evals, 1),
            'num_feedback_session': num_feedback_session,
            'ave_feedback_session': ave_feedback_session
        }
        return Response(data=data)


############## be eval ##############
class BeEvalData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        num_argument = len(Events_agreements.objects.filter(type_report='A', be_evaluated=request.user))
        num_event = len(Events_agreements.objects.filter(type_report='E', be_evaluated=request.user))
        num_open_argument = len(
            Events_agreements.objects.filter(type_report='A', be_evaluated=request.user, is_open_agreement=True))
        num_feedback_session = len(Feedback_sessions.objects.filter(be_evaluated=request.user))
        data = {
            'num_argument': num_argument,
            'num_event': num_event,
            'num_open_argument': num_open_argument,
            'personnel_code': request.user.Personnel_Code,
            'unit': '' if request.user.unit == None else request.user.unit.name,
            'num_feedback_session': num_feedback_session
        }
        return Response({'data': data})


class BeEvalEventArgumentCharts(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chart_argument = self.event_argument_chart(request, 'A')
        chart_event = self.event_argument_chart(request, 'E')
        data = {
            'num_argument': chart_argument,
            'num_event': chart_event
        }
        return Response(data=data)

    def event_argument_chart(self, request, type):
        chart_argument = []
        tmp = 0
        # shwo last 3 manth
        for i in range(3):
            year = JalaliDate.today().year
            month = JalaliDate.today().month - i

            # If it is the first month of the year, the previous month will be the last month of the year
            if month < 1:
                month = month + 12
            # convert to Miladi
            this_month = JalaliDate(year, month, 1).to_gregorian()
            num_this_month = len(
                Events_agreements.objects.filter(date_report__gte=this_month, be_evaluated=request.user,
                                                 type_report=type)) - tmp
            chart_argument.append({'name': self.convert_num_to_month(month), 'value': num_this_month})
            tmp = num_this_month + tmp
        return chart_argument

    def convert_num_to_month(self, month):
        if month == 1: return 'فروردین'
        if month == 2: return 'اردیبهشت'
        if month == 3: return 'خرداد'
        if month == 4: return 'تیر'
        if month == 5: return 'مرداد'
        if month == 6: return 'شهریور'
        if month == 7: return 'مهر'
        if month == 8: return 'آبان'
        if month == 9: return 'آذر'
        if month == 10: return 'دی'
        if month == 11: return 'بهمن'
        if month == 12: return 'اسفند'


class BeEvalAverageEvalFBeginning(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        year = JalaliDate.today().year
        average_eval = []

        # set defult score
        min_score = {'score': 100, 'be_eval': ''}
        max_score = {'score': 0, 'be_eval': ''}

        # The loop continues until we reach a year that has no evaluation.
        while (True):
            evals = Eval_Report.objects.filter(be_evaluated=request.user, year=year, display=True)
            if year == 1400:
                break
            sum = 0

            # Summing up all the evaluations of that year And check min and max
            for eval in evals:
                score = eval.get_score()
                sum = sum + score
                if (score > max_score['score']):
                    max_score['score'] = score
                    max_score['be_eval'] = eval
                if (score < min_score['score']):
                    min_score['score'] = score
                    min_score['be_eval'] = eval
            average = 0 if len(evals) == 0 else sum / len(evals)
            average_eval.append({'year': year, 'average': round(average, 1)})
            year = year - 1

        return Response({'data':
            {
                'min': {
                    'score': '' if min_score['be_eval'] == '' else min_score['be_eval'].get_score()
                },
                'max': {
                    'score': '' if max_score['be_eval'] == '' else max_score['be_eval'].get_score()
                },
                'average_eval': average_eval
            }
        })


class BeEvalAverageEvalCurrent(APIView):
    permission_classes = [IsAuthenticated]

    def get_ave_min_max(self, evals):
        # if it was empty
        if len(evals) == 0:
            return {
                'average': 0,
                'min_score': {'score': 100, 'be_eval': 'nobody'},
                'max_score': {'score': 0, 'be_eval': 'nobody'}
            }

        sum = 0

        # Defult min and max score
        min_score = {'score': 100, 'be_eval': ''}
        max_score = {'score': 0, 'be_eval': ''}
        # Summing up all the evaluations of that evals And check min and max
        for eval in evals:
            score = eval.get_score()
            sum = sum + score
            if (score > max_score['score']):
                max_score['score'] = score
            if (score < min_score['score']):
                min_score['score'] = score
        average = 0 if len(evals) == 0 else sum / len(evals)
        data = {
            'average': round(average, 1),
            'min_score': min_score,
            'max_score': max_score
        }
        return data

    def post(self, request):
        year = JalaliDate.today().year
        data = {
            'bahar': self.get_ave_min_max(
                Eval_Report.objects.filter(be_evaluated=request.user, year=year, season='B', display=True)),
            'tabestan': self.get_ave_min_max(
                Eval_Report.objects.filter(be_evaluated=request.user, year=year, season='T', display=True)),
            'paeez': self.get_ave_min_max(
                Eval_Report.objects.filter(be_evaluated=request.user, year=year, season='P', display=True)),
            'zemestan': self.get_ave_min_max(
                Eval_Report.objects.filter(be_evaluated=request.user, year=year, season='Z', display=True)),
        }

        # Setting the first chapter as total min and max
        total_min = {'score': data['bahar']['min_score']['score'], 'be_eval': data['bahar']['min_score']['be_eval']}
        total_max = {'score': data['bahar']['max_score']['score'], 'be_eval': data['bahar']['max_score']['be_eval']}

        # check min and max
        for key in data:
            if data[key]['max_score']['score'] > total_max['score']:
                total_max['score'] = data[key]['max_score']['score']
                total_max['be_eval'] = data[key]['max_score']['be_eval']
            if data[key]['min_score']['score'] < total_min['score']:
                total_min['score'] = data[key]['min_score']['score']
                total_min['be_eval'] = data[key]['min_score']['be_eval']

        data['min_score'] = total_min
        data['max_score'] = total_max

        return Response({
            'data': data
        })


class BeEvalUserReportTable(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        num_agreements = len(Events_agreements.objects.filter(be_evaluated=request.user, type_report='A'))
        num_event = len(Events_agreements.objects.filter(be_evaluated=request.user, type_report='E'))
        evals = Eval_Report.objects.filter(be_evaluated=request.user, display=True)
        ave_evals = 0
        for eval in evals:
            ave_evals = ave_evals + eval.get_score()
        ave_evals = 0 if len(evals) == 0 else ave_evals / len(evals)
        num_feedback_session = len(Feedback_sessions.objects.filter(be_evaluated=request.user))
        ave_feedback_session = 0
        evals = EvaluationForFeedbackSessions.objects.filter(be_evaluated=request.user)
        for eval in evals:
            ave_feedback_session = ave_feedback_session + eval.get_score()
        ave_feedback_session = 0 if len(evals) == 0 else ave_feedback_session / len(evals)
        season_info = get_season_isEvalTime()
        data = {
            'name': request.user.get_full_name(),
            'personal_code': request.user.Personnel_Code,
            'unit': '' if request.user.unit == None else request.user.unit.name,
            'season': season_info['season'],
            'year': season_info['year'],
            'num_agreements': num_agreements,
            'num_event': num_event,
            'ave_eval': round(ave_evals, 1),
            'num_feedback_session': num_feedback_session,
            'ave_feedback_session': ave_feedback_session
        }
        return Response(data=data)
