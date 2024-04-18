# 운동 도우미, 코드핏 (CodeFit)
>**"Codefit"은 코드(Code)와 피트니스(Fitness)의 결합으로, 소프트웨어 개발과 피트니스의 융합을 의미합니다. <br>
프로그래밍과 운동이라는 두 가지 다른 영역을 함께 생각하고, 조화롭게 결합하여 개인의 건강과 웰빙을 증진하는 것을 목표로 합니다. <br>
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

### 📌 기능
>**마이페이지** <br>
>_1. 로그인, 로그아웃, 회원가입, 회원탈퇴를 제공_ <br>
>_2. 프로필에서 사용자는 자신의 정보를 수정 가능_ <br>
>_3. 비밀번호 찾기 기능은 Email을 입력해 재설정 링크 발송_

>**커뮤니티** <br>
>_1. 게시글 생성, 수정, 삭제, 조회 가능_ <br>
>_2. 게시글의 댓글, 대댓글, 좋아요 기능_ <br>
>_3. 사용자 필요에 따라 첨부파일 추가_

>**운동 정보** <br>
>_1. 운동에 대한 정보 (운동명, 난이도, 운동부위 등..) 조회_ <br>
>_2. 해당 정보는 관리자만 수정 가능_

>**건강 정보** <br>
>_1. 사용자의 최근 건강 정보를 입력 및 조회 가능_ <br>
>_2. 사용자는 맞춤으로 운동 루틴이 생성 및 공유 가능_ <br>
>_3. 사용자가 최근 30일 본인의 식단을 기록 및 조회_

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

### 📏 와이어프레임
>**마이페이지** <br>
>마이페이지 클릭 시
![마이페이지  마 - 마이페이지 클릭 시](https://github.com/soohyun020812/Portfolio_/assets/131852352/21ef29e5-58bb-4039-a7e3-06b22d5d225c)
>내 프로필
![마이페이지  마 - 내 프로필](https://github.com/soohyun020812/Portfolio_/assets/131852352/4f858c14-3e4c-46a3-95c2-a48c4270b349)
>친구 목록
![마이페이지  마 - 친구목록](https://github.com/soohyun020812/Portfolio_/assets/131852352/e9832797-1b38-4846-8276-2e73573d5654)
>내 운동기록
![마이페이지  마 - 내 운동기록](https://github.com/soohyun020812/Portfolio_/assets/131852352/5d8bba12-e9af-436e-b6a0-6f2be0ca0b93)
>찜한 운동
![마이페이지  마 - 찜한 운동](https://github.com/soohyun020812/Portfolio_/assets/131852352/018c8cd5-291b-4771-8dc8-06a0b6a97fab)
>계정 탈퇴
![마이페이지  마 - 계정 탈퇴 (1)](https://github.com/soohyun020812/Portfolio_CodeFit/assets/131852352/044cc168-c47a-4eb5-81fe-da3148b72cac)

>**운동 정보** <br>
>운동 정보 전체
![운동 정보와 건강정보  운 - 운동정보 전체](https://github.com/soohyun020812/Portfolio_/assets/131852352/77334283-aedd-4373-8972-36efcb883473)
>운동 정보 상세
![운동 정보와 건강정보  운 - 운동정보 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/b0e3b641-13e3-4eaf-aab1-92c5de568275)
>관련 운동 추천 상세
![운동 정보와 건강정보  운 - 관련 운동 추천 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/388eab9e-144a-46a0-85f5-cd00cec2005c)

>**커뮤니티** <br>
>커뮤니티 전체
![24 04 02 커뮤니티 와이어프레임  커 - 게시판 전체](https://github.com/soohyun020812/Portfolio_/assets/131852352/29fb467e-ccec-4b80-9a66-6e1758578266)
>커뮤니티 게시글
![24 04 02 커뮤니티 와이어프레임  커 - 게시글 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/ace52e3f-4548-4946-830d-48d7ef1b4509)
>커뮤니티 게시글 상세
![24 04 02 커뮤니티 와이어프레임  커 - 게시글 상세 2](https://github.com/soohyun020812/Portfolio_/assets/131852352/da73a75a-c1c2-465a-be62-62e7228d4252)
>식단 공유 게시판
![24 04 02 커뮤니티 와이어프레임  커 - 식단 공유 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/81e39ad8-408c-4fad-9dd7-eaadf3e5a41c)
>운동 공유 게시판
![24 04 02 커뮤니티 와이어프레임  커 - 운동 공유 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/ed178521-2733-430f-98ee-8b235650280f)
>게시판 댓글
![24 04 02 커뮤니티 와이어프레임  커 - 댓글 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/a299eee4-4fa9-4fdb-a550-cce3dda2396a)
>게시판 대댓글
![24 04 02 커뮤니티 와이어프레임  커 - 대댓글 상세](https://github.com/soohyun020812/Portfolio_/assets/131852352/40d96393-3dcb-4b49-83ae-5a1dcc88c62e)
>게시판 대댓글 상세
![24 04 02 커뮤니티 와이어프레임  커 - 대댓글 상세 2](https://github.com/soohyun020812/Portfolio_/assets/131852352/73e170f7-9055-47f2-9252-0b0f8ae5bb26)

### 💥 트러블슈팅
>**Django 테스트** <br>

>_모델 내용을 변경하지 않고, 그 모델을 참조하는 다른 모델 조회 시 불일치_ <br>
_모델을 변경시킬 때 마다 save()를 통해 변경하여 해결_

>_테스트 코드 내에서 patch, post의 응답을 기존 모델 인스턴스와 비교할 때 불일치_ <br>
_조회할 인스턴스의 refresh_from_db()를 사용하여 해결_

### 💭 프로젝트 회고
```
팀원으로써 이번 프로젝트를 진행하면서 소중한 경험을 쌓았습니다.
특히 팀장님의 역할을 통해 팀원과의 소통이 얼마나 중요한지를 더욱 명확하게 깨닫게 되었습니다.

팀장님은 각자의 능력과 역할을 고려하여 작업을 분배하고 문제가 발생할 때마다 적극적으로 의견을 수렴하고 해결책을 모색해주셨습니다.
이를 통해 프로젝트가 원활하게 진행되었고 팀원들 간의 협업도 더욱 강화되었습니다.

이번 프로젝트를 통해 기술적으로도 많이 성장할 수 있었습니다.

TDD를 처음 접하면서 요구사항을 명확하게 작성하고 코드를 작성하기 전에 테스트 케이스를 먼저 고려하는 중요성을 깨달았습니다.
이를 통해 코드의 품질을 높이고 유지보수성을 향상시킬 수 있었습니다.
그리고 코드의 추상화와 응답을 테스트하는 것이 코드의 유연성을 높이는 데에 도움이 되었습니다.

하지만 아쉬웠던 점도 분명 있었습니다.

TDD를 적용하면서 테스트 코드 작성과 실행에 많은 시간이 소요되었던 것이 아쉬웠습니다.
이로 인해 프로젝트의 진행 속도가 늦어지고, 완료에 영향을 미쳤습니다.
앞으로는 이러한 시간적 제약을 극복하고, 보다 효율적으로 TDD를 적용할 방법을 고민해봐야겠습니다.
```
