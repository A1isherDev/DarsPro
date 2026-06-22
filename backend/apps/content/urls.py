"""DarsPro — /api/content/ marshrutlari."""
from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    ContentItemViewSet,
    EngineListView,
    GradeListView,
    SubjectListView,
    TopicListView,
)

router = SimpleRouter(trailing_slash=False)
router.register("items", ContentItemViewSet, basename="contentitem")

urlpatterns = [
    path("grades", GradeListView.as_view(), name="grades"),
    path("subjects", SubjectListView.as_view(), name="subjects"),
    path("topics", TopicListView.as_view(), name="topics"),
    path("engines", EngineListView.as_view(), name="engines"),
    *router.urls,
]
