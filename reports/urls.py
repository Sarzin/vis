from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path("create_events_agreements/", CreateEventsAgreements.as_view(), name="create_an_event"),
    path("create-feed-back-session/", FeedBack.as_view(), name="create-feed-back-session"),
    path("all-reports/eventsagreements/", ShowAllReportEventsAgreements.as_view(), name="list_of_Events_Agreements"),
    # path("all-reports/events-for-indicator/", ShowAllReportEventsForIndicator.as_view(),
    #      name="list_of_Events_for_indicator"),  # dublicate shode ehtemalan
    path("all-reports/show-all-events-agreements-for-indicator/", ShowAllEventsAgreementsForIndicator.as_view(),
         name="ShowAllEventsAgreementsForIndicator"),
    path("show-all-agreements-open/", ShowAllAgreementsOpen.as_view(), name="ShowAllAgreementsOpen"),
    path("filter-type/", FilterObjBaseType.as_view(), name="filter-type"),
    url(r'^detail/eventsagreements/(?P<id>\d+)$', ShowDetailReportEventsAgreements.as_view(),
        name='detailReportEventsAgreements'),
    path("all-reports/feedback/", FeedBackListAssessorAPIView.as_view(), name="list_of_FeedBack-assesor"),
    url('list-feed-back-session/', FeddBackSessionListBeEvaluatedAPIView.as_view(),
        name='feed_back_session_list_be eval'),
    path('like-or-dislike', LikeOrDislike.as_view(), name='like_or_dislike'),
    path('show-questions-for-feedbackSessions', ShowQuestionsForFeedbackSessions.as_view(),
         name='show-questions-for-feedbackSessions'),
    path('evaluation-for-feedbackSessions', EvaluationForFeedbackSessionsView.as_view(),
         name='evaluation-for-feedbackSessions'),
    path('report-evaluation-for-feedbackSessions', ReportEvaluationForFeedbackSessionsView.as_view(),
         name='report-evaluation-for-feedbackSessions'),

]
