import abc
import random

from faker import Faker
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import CustomUser
from community.models import Post
from exercises_info.models import ExercisesAttribute, ExercisesInfo, FocusArea
from my_health_info.models import (
    ExerciseInRoutine,
    HealthInfo,
    MirroredRoutine,
    Routine,
    RoutineStreak,
    WeeklyRoutine,
    ExerciseInRoutineAttribute,
)
from my_health_info.services import UsersRoutineManagementService
from utils.enums import FocusAreaEnum


class FakeModel(abc.ABC):
    """
    가짜 모델 생성 클래스
    공통된 동작을 정의했습니다.
    """

    def __init__(self, model):
        """생성시 모델을 받아서 인스턴스 변수로 저장합니다."""
        self.fake = Faker()
        self.model = model
        self.attributes = self.model._meta.get_fields()
        self.base_attr = None
        self.related_fake_models = None
        self.related_attr = None
        self.derived_attr = None

    def needed_info(self, info_list):
        """필요한 정보로 이루어진 리스트를 넣으면 필요한 정보와 값을 반환합니다."""
        return {key: self.base_attr.get(key) for key in info_list}

    @abc.abstractmethod
    def set_base_attr(self):
        """모델의 기본 속성을 설정합니다."""
        pass

    def set_related_fake_models(self):
        """모델의 관련 가짜 모델을 설정합니다."""
        pass

    def set_related_attr(self):
        """모델의 관련 속성을 설정합니다."""
        pass

    def set_derived_attr(self):
        """모델의 파생 속성을 설정합니다."""
        pass

    @abc.abstractmethod
    def create_instance(self):
        """모델을 생성하고 인스턴스를 반환합니다."""
        pass

    def request_partial_update(self, **kwargs):
        """Partial Update 요청에 필요한 정보를 반환합니다."""
        for key, value in kwargs.items():
            if key in self.base_attr:
                self.base_attr[key] = value


class FakeUser(FakeModel):
    def __init__(self):
        super().__init__(CustomUser)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
        }

    def create_instance(self, is_staff=False):
        """스태프 여부에 따라 유저를 생성합니다."""
        if is_staff:
            self.instance = self.model.objects.create_superuser(**self.base_attr)
        else:
            self.instance = self.model.objects.create_user(**self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["username", "email", "password"])

    def request_login(self):
        """Login 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["email", "password"])

    def get_jwt_token(self):
        """JWT Token을 반환합니다."""
        if not self.instance:
            return
        jwt_token = RefreshToken.for_user(self.instance)

        self.access_token = jwt_token.access_token

    def login(self, client):
        """JWT Token을 포함한 인증 정보를 반환합니다."""
        if not self.instance:
            return
        if not hasattr(self, "access_token"):
            self.get_jwt_token()

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")


class FakeExerciseInRoutine(FakeModel):
    def __init__(self, order, fake_exercises_info):
        super().__init__(ExerciseInRoutine)
        self.base_attr = self.set_base_attr(order)
        self.related_fake_models = self.set_related_fake_models(fake_exercises_info)
        self.related_attr = self.set_related_attr()

    def set_base_attr(self, order):
        return {
            "order": order,
        }

    def set_related_fake_models(self, fake_exercises_info):
        return {
            "exercises_info": fake_exercises_info,
        }

    def set_related_attr(self):
        return {
            "exercises_info": self.related_fake_models.get(
                "exercises_info"
            ).request_create(),
            "exercise_attribute": {
                "set_count": self.fake.random_int(1, 5),
                "rep_count": self.fake.random_int(1, 20),
                "weight": self.fake.random_int(1, 250),
                "duration": self.fake.random_int(1, 60),
                "speed": self.fake.random_int(1, 15),
            },
        }

    def create_instance(self, routine_instance, mirrored_routine_instance):
        fake_exercise_info = self.related_fake_models.get("exercises_info")

        if not fake_exercise_info.instance:
            return

        self.instance = self.model.objects.create(
            routine=routine_instance,
            mirrored_routine=mirrored_routine_instance,
            exercise=fake_exercise_info.instance,
            **self.base_attr,
        )

        ExerciseInRoutineAttribute.objects.create(
            exercise_in_routine=self.instance,
            **self.related_attr["exercise_attribute"],
        )

        return self.instance

    def request_create(self):
        base_attr = self.base_attr
        related_attr = self.related_attr

        related_attr["exercise"] = self.related_fake_models.get(
            "exercises_info"
        ).instance.id
        related_attr.pop("exercises_info")

        return {**base_attr, **related_attr}


class FakeRoutine(FakeModel):
    def __init__(self, fake_exercises_infos):
        super().__init__(Routine)
        self.base_attr = self.set_base_attr()
        self.related_fake_models = self.set_related_fake_models(fake_exercises_infos)
        self.related_attr = self.set_related_attr()

    def set_base_attr(self):
        return {
            "title": self.fake.sentence(),
        }

    def set_related_fake_models(self, fake_exercises_infos):
        exercises_in_routine = self.set_exercises_in_routine(fake_exercises_infos)
        return {
            "exercises_in_routine": exercises_in_routine,
        }

    def set_exercises_in_routine(self, fake_exercises_infos):
        fake_exercises_in_routine = []

        for order, fake_exercises_info in enumerate(fake_exercises_infos, start=1):
            fake_exercise_in_routine = FakeExerciseInRoutine(order, fake_exercises_info)
            fake_exercises_in_routine.append(fake_exercise_in_routine)

        return fake_exercises_in_routine

    def set_related_attr(self):
        related_attr = {}

        if "exercises_in_routine" in self.related_fake_models:
            related_attr["exercises_in_routine"] = [
                fake_exercise_in_routine.request_create()
                for fake_exercise_in_routine in self.related_fake_models.get(
                    "exercises_in_routine"
                )
            ]

        return related_attr

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            author=user_instance, **self.base_attr
        )

        mirrored_routine = MirroredRoutine.objects.create(
            title=self.instance.title,
            author_name=user_instance.username,
            original_routine=self.instance,
        )

        for fake_exercise_in_routine in self.related_fake_models.get(
            "exercises_in_routine"
        ):
            fake_exercise_in_routine.create_instance(
                routine_instance=self.instance,
                mirrored_routine_instance=mirrored_routine,
            )

        service = UsersRoutineManagementService(
            user=user_instance, routine=self.instance
        )

        service.user_create_routine(mirrored_routine)

        return self.instance

    def request_create(self):
        base_attr = self.base_attr
        related_attr = self.related_attr

        return {**base_attr, **related_attr}


class FakeWeeklyRoutine(FakeModel):
    def __init__(self, day_index, users_routine):
        super().__init__(WeeklyRoutine)
        self.base_attr = self.set_base_attr(day_index)
        self.users_routine = users_routine

    def set_base_attr(self, day_index):
        return {
            "day_index": day_index,
        }

    def create_instance(self, user_instance):
        if not self.users_routine:
            return

        self.instance = self.model.objects.create(
            user=user_instance,
            users_routine=self.users_routine,
            **self.base_attr,
        )

        return self.instance

    def create_request(self):
        base_attr = self.base_attr
        related_attr = {
            "users_routine": self.users_routine.id,
        }

        return {**base_attr, **related_attr}


class FakeRoutineStreak(FakeModel):
    def __init__(self, mirrored_routine):
        super().__init__(RoutineStreak)
        self.base_attr = self.set_base_attr()
        self.mirrored_routine_instance = mirrored_routine

    def set_base_attr(self):
        return {}

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            user=user_instance,
            mirrored_routine=self.mirrored_routine_instance,
            **self.base_attr,
        )

        return self.instance

    def request_create(self):
        return {}


class FakeHealthInfo(FakeModel):
    def __init__(self):
        super().__init__(HealthInfo)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "height": self.fake.random_int(150, 200),
            "weight": self.fake.random_int(50, 100),
            "age": self.fake.random_int(10, 100),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(user=user_instance, **self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        base_info = self.needed_info(["height", "weight", "age"])
        return base_info


class FakeFocusArea(FakeModel):
    def __init__(self, focus_area):
        super().__init__(FocusArea)
        self.base_attr = self.set_base_attr(focus_area)
        self.count = random.randint(1, 4)

    def set_base_attr(self, focus_area):
        return {
            "focus_area": focus_area,
        }

    def create_instance(self):
        self.instance = self.model.objects.create(**self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["focus_area"])


class FakeExercisesAttribute(FakeModel):
    def __init__(self):
        super().__init__(ExercisesAttribute)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "need_set": self.fake.boolean(),
            "need_rep": self.fake.boolean(),
            "need_weight": self.fake.boolean(),
            "need_duration": self.fake.boolean(),
            "need_speed": self.fake.boolean(),
        }

    def create_instance(self):
        self.instance = self.model.objects.create(**self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(
            ["need_set", "need_rep", "need_weight", "need_duration", "need_speed"]
        )


class FakeExercisesInfo(FakeModel):
    def __init__(self):
        super().__init__(ExercisesInfo)
        self.base_attr = self.set_base_attr()
        self.related_fake_models = self.set_related_fake_models()
        self.related_attr = self.set_related_attr()

    def set_base_attr(self):
        return {
            "title": self.fake.sentence(),
            "description": self.fake.text(),
            "video": self.fake.url(),
        }

    def set_related_fake_models(self):
        focus_areas = self.set_focus_areas()
        exercises_attribute = FakeExercisesAttribute()
        return {
            "focus_areas": focus_areas,
            "exercises_attribute": exercises_attribute,
        }

    def set_focus_areas(self):
        sample_count = random.randint(1, 4)
        sample_focus_areas = random.sample(FocusAreaEnum.choices(), sample_count)

        focus_areas = []
        for name, area in sample_focus_areas:
            fake_focus_area = FakeFocusArea(area)
            focus_areas.append(fake_focus_area)

        return focus_areas

    def set_related_attr(self):
        related_attr = {}

        if not self.related_fake_models:
            return related_attr

        if "focus_areas" in self.related_fake_models:
            related_attr["focus_areas"] = [
                focus_area.request_create()
                for focus_area in self.related_fake_models.get("focus_areas")
            ]

        if "exercises_attribute" in self.related_fake_models:
            related_attr["exercises_attribute"] = self.related_fake_models[
                "exercises_attribute"
            ].base_attr

        return related_attr

    def create_instance(self, user_instance):
        fake_exercises_attribute = self.related_fake_models.get("exercises_attribute")
        exercises_attribute_instance = fake_exercises_attribute.create_instance()

        self.instance = self.model.objects.create(
            author=user_instance,
            **self.base_attr,
            exercises_attribute=exercises_attribute_instance,
        )

        fake_focus_areas = self.related_fake_models.get("focus_areas")

        fake_focus_area_instances = []
        for fake_focus_area in fake_focus_areas:
            instance = fake_focus_area.create_instance()
            fake_focus_area_instances.append(instance)

        self.instance.focus_areas.set(fake_focus_area_instances)

        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        base_attr = self.base_attr
        related_attr = self.related_attr
        return {**base_attr, **related_attr}


class FakePost(FakeModel):
    def __init__(self):
        super().__init__(Post)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "title": self.fake.sentence(),
            "content": self.fake.text(),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            author=user_instance, **self.base_attr
        )
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["title", "content"])
