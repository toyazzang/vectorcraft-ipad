# VectorCraft iPad 웹앱 (오프라인 지원, 자동 업데이트)

VectorCraft 공식 웹 빌드(`vectorcraft-web-*.zip`)를 내 GitHub Pages에 올리고, iPad 홈 화면 앱으로 설치해서
인터넷 없이도 쓰는 구성입니다. 업스트림에 새 릴리스가 나오면 매일 한 번 자동으로 가져와 배포합니다.

## 한 번만 하는 설정 (GitHub 웹에서, 약 10분)

1. GitHub에서 **새 저장소**를 만듭니다. 이름은 자유(예: `vectorcraft-ipad`), **Public**.
   (무료 계정은 Public 저장소만 Pages를 쓸 수 있습니다. 올라가는 것은 공개된 오픈소스 앱뿐이고, 내 작업 파일은 올라가지 않습니다.)
2. 이 폴더의 파일을 저장소에 올립니다. `Add file → Upload files`로 `scripts/`, `templates/`, `.github/`, `README.md`를 끌어다 놓습니다.
   `.github` 폴더가 안 보이거나 안 올라가면 `Add file → Create new file`에서 이름 칸에 `.github/workflows/deploy.yml`을 입력하고 내용을 붙여넣으세요.
3. 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
4. **Actions** 탭 → `Deploy VectorCraft (iPad web app)` → **Run workflow**. 2~3분 뒤 초록색 체크가 뜨면 끝입니다.
   주소는 `https://<내 GitHub 아이디>.github.io/<저장소 이름>/` 입니다.

## iPad에서 설치 (인터넷이 되는 곳에서 한 번)

1. **Safari**로 위 주소를 엽니다. 첫 로딩은 파일이 커서(앱 본체 약 67 MB, 서버가 압축해서 보내면 약 23 MB) 시간이 걸립니다. 와이파이에서 하세요.
2. 공유 버튼 → **홈 화면에 추가**.
3. **홈 화면의 아이콘으로 한 번 실행**하고, 앱이 뜬 뒤 1~2분 기다립니다. 이때 오프라인용 사본이 저장됩니다.
4. 비행기 모드를 켜고 다시 실행해서 열리는지 확인하세요. 여기까지 되면 이후로는 인터넷 없이 쓸 수 있습니다.

다른 iPad도 같은 주소로 같은 방법으로 설치하면 됩니다.

## 업데이트

- GitHub가 매일 새 릴리스를 확인해서 자동으로 배포합니다. 바로 받고 싶으면 Actions 탭에서 Run workflow.
- iPad는 **인터넷이 연결된 상태에서 앱을 열면** 백그라운드로 새 버전을 받고, **다음 실행부터** 적용됩니다.
- 인터넷이 없으면 지금 설치된 버전을 계속 씁니다.

## 알아둘 점

- **파일 저장**: 저장과 내보내기는 다운로드 방식이라 파일이 Files 앱에 저장됩니다. 열기는 파일 선택 창을 씁니다. 오프라인에서도 됩니다.
- **오프라인 보관**: iOS는 오랫동안 안 쓴 웹 데이터를 지울 수 있습니다. 홈 화면 앱은 대개 괜찮지만, 중요한 출장 전에는 비행기 모드로 한 번 열어 확인하세요.
  Safari 설정에서 "방문 기록 및 웹사이트 데이터 지우기"를 누르면 오프라인 사본도 지워지니 다시 설치해야 합니다.
- **스케줄 중단**: Public 저장소는 60일 동안 활동이 없으면 GitHub가 매일 실행을 멈춥니다. 멈추면 Actions 탭에서 Enable 후 Run workflow.
- **렌더링 문제**: 화면이 깨지면 주소 끝에 `?webgl` (또는 `?cpu`)을 붙여 열어 보세요. 오프라인 캐시도 그대로 동작합니다.
- **상표**: 업스트림 파일은 수정하지 않고 `index.html`에 오프라인용 3줄만 추가합니다. 코드를 고쳐 공개 배포할 계획이면 ArtCraft 이름과 로고 규칙을 확인하세요.

## 구성

| 파일 | 역할 |
|---|---|
| `.github/workflows/deploy.yml` | 최신 릴리스 다운로드, 체크섬 검증, 사이트 빌드, Pages 배포 |
| `scripts/build_site.py` | 업스트림 웹 빌드에 오프라인 캐시 등록 코드 추가 |
| `templates/sw.template.js` | 서비스 워커(오프라인 캐시) |
| `templates/manifest.webmanifest`, `templates/icons/` | 홈 화면 앱 정보와 아이콘 |
