from rest_framework.serializers import ModelSerializer
from .models import *


class EventSerializer(ModelSerializer):
    # def show_event_for_evaluated_user(self):

    class Meta:
        model = Events_agreements
        exclude = ('assessor',)


class FeedBackSerializer(ModelSerializer):
    class Meta:
        model = Feedback_sessions
        fields = ('id', 'description', 'be_evaluated', 'date_report', 'description_hidden')


class ShowAllReportSerializer(ModelSerializer):
    class Meta:
        model = Events_agreements
        fields = (
            'be_evaluated', 'assessor', 'id', 'type_report', 'assessment_type', 'description', 'date_report',
            'indicators', 'is_open_agreement', 'deadline', 'like_dislike', 'be_seen')


class LikeDislikeSerializer(ModelSerializer):
    class Meta:
        model = Events_agreements
        fields = (
            'id', 'like_dislike'
        )


class ReportEvalForFeedbackSessionsSerializer(ModelSerializer):
    class Meta:
        model = EvaluationForFeedbackSessions
        fields = '__all__'


class QuestionForFeedbackSessionsSerializer(ModelSerializer):
    class Meta:
        model = QuestionForFeedbackSessions
        fields = '__all__'
