from django.db import models

from account.models import CustomUser as User


class FocusArea(models.Model):
    focus_area = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.focus_area}"


class ExercisesAttribute(models.Model):
    need_set = models.BooleanField(default=False)
    need_rep = models.BooleanField(default=False)
    need_weight = models.BooleanField(default=False)
    need_duration = models.BooleanField(default=False)
    need_speed = models.BooleanField(default=False)

    def __str__(self):
        return f"NeedSet: {self.need_set}\nNeedRep: {self.need_rep}\nNeedWeight: {self.need_weight}\nNeedDuration: {self.need_duration}\nNeedSpeed: {self.need_speed}"


class ExercisesInfo(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exercises_info"
    )
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    video = models.CharField(max_length=200)

    focus_areas = models.ManyToManyField(
        FocusArea,
        related_name="exercises_info",
        blank=True,
    )

    exercises_attribute = models.OneToOneField(
        ExercisesAttribute,
        on_delete=models.CASCADE,
        related_name="exercises_info",
    )

    def __str__(self):
        return f"{self.title}"

    def delete(self, *args, **kwargs):
        self.exercises_attribute.delete()
        super().delete(*args, **kwargs)
