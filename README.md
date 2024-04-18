# 운동 도우미, 코드핏 (CodeFit)
>**"Codefit"은 코드(Code)와 피트니스(Fitness)의 결합으로, 소프트웨어 개발과 피트니스의 융합을 의미합니다. <br>
이는 프로그래밍과 운동이라는 두 가지 다른 영역을 함께 생각하고, 조화롭게 결합하여 개인의 건강과 웰빙을 증진하는 것을 목표로 합니다. <br>
코드의 정확성과 효율성을 개발하며 동시에 건강한 신체를 유지하기 위한 운동을 통합하여, 개발자들이 건강한 라이프스타일을 유지하고 지속적인 성장을 이룰 수 있도록 돕는 개념입니다.**

### 💻 프로젝트 소개
>**Django Final Project** <br>
>**운동 도우미 웹, 앱 서비스입니다.** <br>
>**사용자는 자신의 운동 기록을 관리할 수 있으며 남들과 소통할 수 있습니다.** <br>
>**등록된 운동들을 조합해 자신만의 루틴 생성이 가능하며 공유할 수 있습니다.** <br>
>**사용자의 편의에 따라 특정 요일에 운동을 직접 배치해 사용자의 주간 루틴을 생성합니다.**

### 🧠 개발 동기
>**운동은 많은 사람들이 즐기는 활동이며, 팀원들도 운동을 즐기는 사람들이었습니다. <br>
또한, 팀장의 지인이 트레이너라는 점은 운동 코칭에 대한 직접적인 조언을 얻을 수 있는 좋은 기회가 될 수 있다 생각하였습니다.**

### 🕰 개발 기간
>**2024-03-29 ~ 2024-04-17**

### 👥 개발 인원
>**팀장 : 최지석** <br>
>**팀원 : 안효준, 이수현, 임빈**

### ✨ 구현 역할
>**팀장 : 최지석** <br>
>_요구사항 취합 및 정리_ <br>
>_Url Mapping 기초 설계_ <br>
>_CI & CD_ <br>
>_MyHealthInfo App_ <br>
>_ExercisesInfo App_

>**팀원 : 안효준** <br>
>_프로젝트 문서화_ <br>
>_Profile App_

>**팀원 : 이수현** <br>
>_fe 디자인 (Figma)_ <br>
>_와이어프레임_ <br>
>_Community App_

>**팀원 : 임빈** <br>
>_프로젝트 문서화_ <br>
>_ExercisesInfo App_

### 🔎 WBS
>**일정표는 머메이드로 작성**
```mermaid
gantt
    title CodeFit 개발 일정
    dateFormat YY-MM-DD
    axisFormat %Y-%m-%d

    section 기획
    아이디어 논의 및 기획 : des1, 2024-03-29, 3d
    요구사항 취합 : des2, after des1, 2d
    데이터베이스 설계 : des3, after des2, 3d

    section 와이어프레임
    와이어프레임 제작 : des11, 2024-04-7, 1d

    section 백엔드 개발
    Account 모듈 개발 : des4, after des3, 3d
    Community 모듈 개발 : des5, after des4, 3d
    MyHealthInfo 모듈 개발 : des6, after des5, 3d
    ExerciseInfo 모듈 개발 : des7, after des6, 2d

    section 프론트엔드 개발
    프론트엔드 개발 : des8, after des3, 11d

    section CICD
    CI/CD 설정 및 구성 : des9, after des6, 3d

    section 마무리
    마무리 : des10, 2024-04-17, 1d
```

### 🚀 사용 기술 스택
>**Frontend** <br>
<img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=Flutter&logoColor=white"> <img src="https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=Dart&logoColor=white"> <img src="https://img.shields.io/badge/Material Design-757575?style=for-the-badge&logo=Material-Design&logoColor=white">

>**Backend** <br>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white"> <img src="https://img.shields.io/badge/Django Rest Framework-092E20?style=for-the-badge&logo=Django&logoColor=white">

>**InfraStructure** <br>
<img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=Amazon AWS&logoColor=white"> <img src="https://img.shields.io/badge/NGINX-269539?style=for-the-badge&logo=NGINX&logoColor=white"> <img src="https://img.shields.io/badge/Gunicorn-342D7E?style=for-the-badge&logo=Gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=Firebase&logoColor=black">

>**Project Management** <br>
<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white"> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white"> <img src="https://img.shields.io/badge/Notion-ffffff?style=for-the-badge&logo=Notion&logoColor=black"> <img src="https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=Figma&logoColor=white">

### 🌐 Diagram
>**Entity-Relationship Diagram**
```mermaid
erDiagram
%%account
    User {
        int id PK
        str email UK
        str username UK
        str password
        int last_health_info FK "HealthInfo_id"
        datetime created_at
    }

    User ||--o| HealthInfo : last_health_info
%%my_health_info
    HealthInfo {
        int id PK
        int user FK "User_id"
        int age
        float weight
        float height
        date date
    }

    HealthInfo }|--|| User : user

    Routine {
        int id PK
        int author FK "User_id"
        str title
        int liked_users FK "User_id"
        int like_count
    }

    Routine }|--o| User : author
    Routine }|--o{ User : liked_users

    MirroredRoutine {
        int id PK
        int original_routine FK "Routine_id"
        str title
        str authored_name
    }

    MirroredRoutine ||--o| Routine : original_routine
%%exercises_info
    ExercisesInfo {
        int id PK
        int author FK "User_id"
        str name
        str description
        str video_url
    }

    ExercisesInfo }|--|| User : author

    FocusArea {
        int id PK
        int exercise FK "Exercise_id"
        str focus_area
    }

    FocusArea }|--|| ExercisesInfo : exercise

    ExerciseAttribute {
        int id PK
        int exercise FK "Exercise_id"
        bool need_set
        bool need_rep
        bool need_weight
        bool need_speed
        bool need_duration
    }

    ExerciseAttribute ||--|| ExercisesInfo : exercise
%%my_healhth_info
    ExerciseInRoutine {
        int id PK
        int routine FK "Routine_id"
        int mirrored_routine FK "MirroredRoutine_id"
        int exercise FK "Exercise_id"
        int order
    }

    ExerciseInRoutine }|--o| Routine : routine
    ExerciseInRoutine }|--|| MirroredRoutine : mirrored_routine
    ExerciseInRoutine }|--|| ExercisesInfo : exercise

    ExerciseInRoutineAttribute {
        int id PK
        int exercise_in_routine FK "ExerciseInRoutine_id"
        int set
        int rep
        float weight
        float speed
        float duration
    }

    ExerciseInRoutineAttribute ||--|| ExerciseInRoutine : exercise_in_routine

    UsersRoutine {
        int id PK
        int user FK "User_id"
        int routine FK "Routine_id"
        int mirrored_routine FK "MirroredRoutine_id"
        bool is_author
        bool need_update
    }

    UsersRoutine }|--|| User : user
    UsersRoutine }|--o| Routine : routine
    UsersRoutine }|--|| MirroredRoutine : mirrored_routine

    RoutineStreak {
        int id PK
        int user_id FK "User_id"
        int mirrored_routine FK "MirroredRoutine_id"
        date date
    }

    RoutineStreak }|--|| User : user
    RoutineStreak }|--o| MirroredRoutine : mirrored_routine

    WeeklyRoutine {
        int id PK
        int user FK "User_id"
        int day_index
        int users_routine FK "UsersRoutine_id"
    }

    WeeklyRoutine }|--|| User : user
    WeeklyRoutine }|--|| UsersRoutine : users_routine
%%community
    Post {
        int id PK
        int author FK "User_id"
        str title
        str content
        int liked_users FK "User_id"
        int like_count
    }

    Post }o--|| User : author
    Post }o--o{ User : liked_users

    Comment {
        int id PK
        int author FK "User_id"
        int post FK "Post_id"
        str content
    }

    Comment }o--|| User : author
    Comment }o--|| Post : post

    SubComment {
        int id PK
        int author FK "User_id"
        int comment FK "Comment_id"
        str content
    }

    SubComment }o--|| User : author
    SubComment }o--|| Comment : comment
```
