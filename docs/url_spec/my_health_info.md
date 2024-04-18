# My Health Info Url Specification

## /my-health-info

### GET

#### Request

| Parameter | Type | Description |
|-----------|------|-------------|
|           |      |             |

#### Response

| Parameter | Type | Description |
|-----------|------|-------------|
| weight    | float| 사용자의 몸무게 |
| height    | float| 사용자의 키 |
| age       | int  | 사용자의 나이 |
| bmi       | float| 사용자의 BMI |
| created_at| datetime| 정보 생성 시간 |

### /routine/

#### GET

#### Request

#### Response

```python
routine_format = {
    id: 1,
    title: "루틴 제목",
    author: {
        username: "유저 이름",
        email: "유저 이메일",
    },
    username: "유저 이름",
    created_at: "2021-01-01T00:00:00",
    like_count: 0,
    exercises_in_routine: [
        {
            id: 1,
            order: 0,
            exercise: {
                id: 1,
                title: "운동 제목",
                description: "운동 설명",
                video: "https://www.youtube.com/watch?v=12345",
                focus_areas: [
                    {
                        id: 1,
                        name: "하체",
                    }
                ],
                exercises_attribute: {
                    id: 1,
                    need_set: True,
                    need_rep: True,
                    need_weight: False,
                    need_duration: False,
                    need_speed: False,
                },
            },
            exercise_attribute: {
                id: 1,
                set_count: 3,
                rep_count: 10,
                weight: 0,
                duration: 0,
                speed: 0,
            },
        }
    ],
}
```
