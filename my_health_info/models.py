from django.db import models

from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo


class HealthInfo(models.Model):
    """
    유저의 건강 정보를 저장하는 모델

    user: 유저 정보
    age: 나이
    height: 키
    weight: 몸무게
    date: 건강 정보 생성일
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username}의 건강 정보"


class Routine(models.Model):
    """
    루틴을 저장하는 모델

    author: 루틴의 작성자
    title: 루틴 제목
    created_at: 루틴 생성일
    liked_users: 루틴을 좋아하는 유저
    like_count: 루틴 좋아요 수
    """

    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_routines"
    )
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    liked_users = models.ManyToManyField(
        User,
        related_name="liked_routines",
    )
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.author.username}이 작성한 루틴: {self.title}, 좋아요 수: {self.like_count}"


class MirroredRoutine(models.Model):
    """
    루틴의 정보를 복제하여 저장하고 original_routine 필드로 원본 루틴을 참조하는 모델

    설계 목적: 루틴을 복제하여 저장함으로써 사용자가 사용하는 루틴 데이터가
    원본 루틴의 변경사항에 영향을 받지 않게 하고, 무결성을 유지하기 위함

    title: 루틴 제목
    author_name: 루틴 작성자 이름
    original_routine: 원본 루틴
    """

    title = models.CharField(max_length=50)
    author_name = models.CharField(max_length=50)
    original_routine = models.OneToOneField(
        Routine, related_name="mirrored_routine", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.author_name}의 루틴: {self.title}"


class ExerciseInRoutine(models.Model):
    """
    루틴에 포함된 운동을 저장하는 모델

    routine: 루틴
    mirrored_routine: mirrored_routine 객체
    exercise: 운동 정보
    order: 운동 순서
    """

    routine = models.ForeignKey(
        Routine,
        related_name="exercises_in_routine",
        on_delete=models.SET_NULL,
        null=True,
    )
    mirrored_routine = models.ForeignKey(
        MirroredRoutine,
        related_name="exercises_in_routine",
        on_delete=models.CASCADE,
    )
    exercise = models.ForeignKey(
        ExercisesInfo,
        related_name="exercises_in_routine",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = (("routine", "order"), ("mirrored_routine", "order"))

    def __str__(self):
        if self.routine:
            return (
                f"{self.routine.title}의 {self.order}번째 운동: {self.exercise.title}"
            )
        else:
            return f"{self.mirrored_routine.title}의 {self.order}번째 운동: {self.exercise.title}"


class ExerciseInRoutineAttribute(models.Model):
    """
    ExerciseInRoutine에 대한 수행 정보를 저장하는 모델

    exercise_in_routine: ExerciseInRoutine 객체
    set_count: 세트 수
    rep_count: 반복 횟수
    weight: 중량
    duration: 운동 시간
    speed: 운동 속도
    """

    exercise_in_routine = models.OneToOneField(
        ExerciseInRoutine, on_delete=models.CASCADE, related_name="exercise_attribute"
    )
    set_count = models.IntegerField(blank=True, default=0)
    rep_count = models.PositiveIntegerField(blank=True, default=0)
    weight = models.FloatField(blank=True, default=0)
    duration = models.PositiveIntegerField(blank=True, default=0)
    speed = models.FloatField(blank=True, default=0)

    class Meta:
        unique_together = ["exercise_in_routine"]

    def __str__(self):
        return f"{self.exercise_in_routine.exercise.title}의 수행 정보"


class UsersRoutine(models.Model):
    """
    유저가 작성하거나 구독한 루틴을 저장하는 모델

    user: 유저
    routine: 루틴
    mirrored_routine: 복제된 루틴
    need_update: 루틴 업데이트 필요 여부
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_author = models.BooleanField(default=False)
    routine = models.ForeignKey(
        Routine,
        related_name="subscribers",
        on_delete=models.SET_NULL,
        null=True,
    )
    mirrored_routine = models.ForeignKey(
        MirroredRoutine,
        related_name="mirrored_subscribers",
        on_delete=models.CASCADE,
    )
    need_update = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "routine"), ("user", "mirrored_routine"))

    def __str__(self):
        if self.routine:
            return f"{self.user.username}의 구독 루틴: {self.routine.title}, 상태: {self.need_update}"
        else:
            return f"{self.user.username}의 구독 루틴: {self.mirrored_routine.title}, 상태: {self.need_update}"


class WeeklyRoutine(models.Model):
    """
    유저의 요일별 루틴을 저장하는 모델

    user: 유저
    users_routine: 유저가 소유한 루틴
    day_index: 요일 인덱스(0: 월요일, 1: 화요일, ..., 6: 일요일)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    users_routine = models.ForeignKey(UsersRoutine, on_delete=models.CASCADE)
    day_index = models.PositiveIntegerField()

    class Meta:
        unique_together = ["user", "day_index"]

    def __str__(self):
        return f"{self.user.username}의 {self.day_index}번째 요일 루틴: {self.users_routine.mirrored_routine.title}"


class RoutineStreak(models.Model):
    """
    해당 날짜의 루틴 수행 여부를 나타내는 모델

    user: 유저
    date: 날짜
    mirrored_routine: 해당 날짜에 수행된 복제된 루틴
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    mirrored_routine = models.ForeignKey(
        MirroredRoutine, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username}가 {self.date}날짜에 {self.mirrored_routine.title} 루틴 수행"
