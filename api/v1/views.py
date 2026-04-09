from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import (
    ChoiceSerializer,
    ChoiceWriteSerializer,
    PollCreateSerializer,
    PollDetailSerializer,
    PollListSerializer,
    PollPartialUpdateSerializer,
    QuestionSerializer,
    QuestionWriteSerializer,
)
from polls.models import Choice, Poll, Question


class PollViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):
        return Poll.objects.filter(owner=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return PollCreateSerializer
        if self.action in ("partial_update", "update"):
            return PollPartialUpdateSerializer
        if self.action == "retrieve":
            return PollDetailSerializer
        return PollListSerializer

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        poll = self.get_object()
        poll.is_published = True
        poll.save(update_fields=["is_published", "updated_at"])
        poll.refresh_from_db()
        return Response(PollDetailSerializer(poll).data)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        poll = self.get_object()
        poll.is_published = False
        poll.save(update_fields=["is_published", "updated_at"])
        poll.refresh_from_db()
        return Response(PollDetailSerializer(poll).data)


class QuestionViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):
        qs = Question.objects.filter(poll__owner_id=self.request.user.id)
        poll_pk = self.kwargs.get("poll_pk")
        if poll_pk is not None:
            return qs.filter(poll_id=poll_pk).order_by("order")
        return qs.order_by("order")

    def get_serializer_class(self):
        if self.action in ("create", "partial_update", "update"):
            return QuestionWriteSerializer
        return QuestionSerializer

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        poll_pk = self.kwargs["poll_pk"]
        poll = get_object_or_404(Poll, pk=poll_pk, owner_id=self.request.user.id)
        serializer.save(poll=poll)


class ChoiceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        qs = Choice.objects.filter(
            question__poll__owner_id=self.request.user.id,
        )
        qpk = self.kwargs.get("question_pk")
        if qpk is not None:
            return qs.filter(question_id=qpk).order_by("order")
        return qs.order_by("order")

    def get_serializer_class(self):
        if self.action == "create":
            return ChoiceWriteSerializer
        return ChoiceSerializer

    def perform_create(self, serializer):
        q_id = self.kwargs["question_pk"]
        question = get_object_or_404(
            Question,
            pk=q_id,
            poll__owner_id=self.request.user.id,
        )
        serializer.save(question=question)


class ChoiceDetailViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ("patch", "delete", "head", "options")
    serializer_class = ChoiceWriteSerializer

    def get_queryset(self):
        return Choice.objects.filter(question__poll__owner_id=self.request.user.id)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().partial_update(request, *args, **kwargs)
