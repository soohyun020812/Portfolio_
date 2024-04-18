from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from exercises_info.models import ExercisesInfo, FocusArea
from exercises_info.serializers import ExercisesInfoSerializer, FocusAreaSerializer


class ExercisesInfoViewSet(viewsets.ModelViewSet):
    queryset = ExercisesInfo.objects.all()
    serializer_class = ExercisesInfoSerializer

    def get_permissions(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
