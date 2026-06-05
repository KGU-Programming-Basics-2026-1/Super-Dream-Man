# Kiryong Campus Platformer Prototype

경기대학교를 배경 콘셉트로 한 도트풍 2D 플랫폼 게임 프로토타입입니다.

## 실행

```powershell
python main.py
```

## 조작

- `←` / `→`: 좌우 이동
- `Space`: 점프
- `↓`: 엎드리기
- `↑`: 고개 위로 들기
- `R`: 월드 재시작
- `Esc`: 월드 선택 또는 이전 화면

## 현재 구현

- 메인 화면: 코스튬 선택 / 월드 선택
- 하늘, 구름, 새가 움직이는 도트풍 분위기
- 기룡이 콘셉트 플레이어의 대기, 달리기, 점프, 엎드리기, 위 보기 모션
- 마리오류 플랫폼 감각을 위한 가속, 감속, 중력, 짧은 점프, 코요테 타임, 점프 버퍼
- 5개 월드 맵
  - 인문대학
  - 자연과학 대학
  - 예술 대학
  - 소프트웨어경영 대학
  - 창의공과 대학

# Super-Dream-Man
아래 두개 링크 들어가서 코드 작성 및 키밋 메세지 작성할 떄 저기에 맞게 작성하고 있는지 확인하고 작성하세요 이슈넘버는 아래 Git Workflow Guide를 따라하시면 됩니다.
## python coding standard
https://peps.python.org/pep-0008/
## conventinal commit
https://www.conventionalcommits.org/en/v1.0.0/

# 🛠 **Git Workflow Guide (Visual C++ in Visual Studio)**

This workflow explains how to manage issues, branches, commits, and pull requests when developing **C++ projects in Visual Studio** using GitHub.

---

## ✅ **1. Create an Issue on GitHub**
*   Go to your repository → **Issues**.
*   Click **New Issue**, write the title & description.
*   Note the **issue number** (example: `#22`).

---

## ✅ **2. Create a Branch on GitHub**
*   Go to the **Code** tab.
*   Make sure the base branch is **main**.
*   Create a new branch named:

```
issue-<issue-number>
```

**Example:**  
```
issue-22
```

---

### ✔ Up to this point, all work is done in the GitHub web browser

---

# 🖥 **Now Move to Visual Studio (Visual C++)**

Visual Studio has built‑in Git tools, but you can also use the terminal.  
Below is the workflow using the **terminal**, which is more reliable and consistent.

---

## ✅ **3. Open Visual Studio and Check Your Current Branch**

In Visual Studio:

*   Open your solution (`.sln`)
*   Open **View → Terminal** or **Developer PowerShell**

Then run:

```bash
git status
```

---

## ✅ **4. Switch to the Base Branch (main)**

```bash
git checkout main
```

---

## ✅ **5. Fetch the Latest Branch Information**

```bash
git fetch
```

---

## ✅ **6. Pull the Latest Changes**

```bash
git pull
```

---

## ✅ **7. Switch to Your New Branch**

```bash
git checkout issue-<issue-number>
```

---

## ✅ **8. Confirm You’re on the Correct Branch**

```bash
git status
```

---

### ✔ Up to this point: all steps are performed in the Visual Studio terminal

---

# 🧑‍💻 **9. Do Your C++ Development Work**
Inside Visual Studio:

*   Edit `.cpp`, `.h`, `.vcxproj` files
*   Build the project
*   Run and debug
*   Test your changes

---

## ✅ **10. Check Branch Before Committing**

```bash
git status
```

---

## ✅ **11. Stage Your Changes**

```bash
git add .
```

---

## ✅ **12. Commit Your Work**

Commit message format:

```
<label>: <description> #<issue-number>
```

**Examples:**

```bash
git commit -m "fix: resolve buffer overflow in parser #22"
git commit -m "feat: add logging module #22"
```

---

## ✅ **13. Push Your Branch to GitHub**

```bash
git push
```

---

### ✔ This is also done in the Visual Studio terminal

---

# 🔀 **14. Create a Pull Request**
On GitHub:

*   Go to **Pull Requests**
*   Click **New Pull Request**
*   Make sure the **base branch** is `main`
*   Submit the PR for review

---

# 🎯 **Tips for Visual Studio + Git**
*   Visual Studio’s Git UI is convenient, but the **terminal is more predictable**.
*   Always update `main` before starting new work.
*   Keep branches small and focused on one issue.
*   Delete your branch after merging to keep the repo clean.

---



