from account.models import CustomUser as User
from my_health_info.models import Routine, UsersRoutine
from my_health_info.serializers import (
    RoutineSerializer,
    MirroredRoutineSerializer,
    UsersRoutineSerializer,
)
from my_health_info.models import MirroredRoutine


class UsersRoutineManagementService:
    """
    Routine 모델의 변경으로 인한 UsersRoutine 모델의 변경을 담당하는 서비스 클래스
    """

    def __init__(self, user, routine):
        self.user = user
        self.routine = routine

    def user_subscribe_routine(self):
        """
        등록된 유저가 등록된 루틴을 구독하는 메서드

        만약 이미 구독 중인 루틴이라면, 이미 구독 중이라는 에러를 발생시킨다.
        만약 작성자 본인의 루틴을 구독하려고 한다면, 작성자 본인의 루틴을 구독할 수 없다는 에러를 발생시킨다.
        """

        if self.user == self.routine.author:
            raise ValueError("자신의 루틴을 구독할 수 없습니다.")
        if UsersRoutine.objects.filter(user=self.user, routine=self.routine).exists():
            raise ValueError("이미 구독 중인 루틴입니다.")

        users_routine = UsersRoutine.objects.create(
            user=self.user,
            routine=self.routine,
            mirrored_routine=self.routine.mirrored_routine,
        )

        return users_routine

    def user_create_routine(self, mirrored_routine):
        """
        유저가 루틴을 생성했을 때, UsersRoutine 모델에도 등록하는 메서드
        """

        users_routine = UsersRoutine.objects.create(
            user=self.user,
            routine=self.routine,
            mirrored_routine=mirrored_routine,
            is_author=True,
        )

        return users_routine
