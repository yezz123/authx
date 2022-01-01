# Release Notes 🎞

## 0.2.0

## What's Changed

### Middleware - Oauth2

The OAuth 2.0 authorization framework is a protocol that allows a user to grant a third-party website or application access to the user's protected resources, without necessarily revealing their long-term credentials or even their identity.

Starlette middleware for authentication through oauth2's via a secret key, which is often used to add authentication and authorization to a web application that interacts with an API on behalf of the user.

That's why AuthX provides a Configuration `MiddlewareOauth2` to configure the OAuth2 middleware.

```py
from authx import MiddlewareOauth2

class AuthenticateMiddleware(MiddlewareOauth2):
    PUBLIC_PATHS = {"/public"}
```

### Code Enhancement

* Remove unnecessary calls to `enumerate` when the index variable is not used. by @yezz123 in <https://github.com/yezz123/authx/pull/179>
* chore: Create a Basic Example to serve the utility of AuthX by @yezz123 in <https://github.com/yezz123/authx/pull/178>
* Clean DocString & Define Functions by @yezz123 in <https://github.com/yezz123/authx/pull/189>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.4...0.2.0>

## 0.1.4

## What's Changed

* Chore(deps-dev): Bump pymdown-extensions from 9.0 to 9.1 by @dependabot in <https://github.com/yezz123/authx/pull/155>
* empty Scheduled daily dependency update on Monday by @pyup-bot in <https://github.com/yezz123/authx/pull/156>
* empty Scheduled daily dependency update on Tuesday by @pyup-bot in <https://github.com/yezz123/authx/pull/157>
* chore: add FastAPI to Classifiers by @yezz123 in <https://github.com/yezz123/authx/pull/163>
* Chore: Fix CI & Delete Docker Configuration ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/165>
* empty Scheduled daily dependency update on Monday by @pyup-bot in <https://github.com/yezz123/authx/pull/166>
* empty Scheduled daily dependency update on Monday by @pyup-bot in <https://github.com/yezz123/authx/pull/167>
* CI: Ignore some Directories 🪨  by @yezz123 in <https://github.com/yezz123/authx/pull/168>
* empty Scheduled daily dependency update on Wednesday by @pyup-bot in <https://github.com/yezz123/authx/pull/169>
* empty Scheduled daily dependency update on Thursday by @pyup-bot in <https://github.com/yezz123/authx/pull/170>
* empty Scheduled daily dependency update on Saturday by @pyup-bot in <https://github.com/yezz123/authx/pull/171>
* empty Scheduled daily dependency update on Wednesday by @pyup-bot in <https://github.com/yezz123/authx/pull/172>
* empty Scheduled daily dependency update on Friday by @pyup-bot in <https://github.com/yezz123/authx/pull/173>
* empty Scheduled daily dependency update on Sunday by @pyup-bot in <https://github.com/yezz123/authx/pull/174>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.3...0.1.4>

## 0.1.3

* Fix the issue relate to PyJWT (Bumping version #151 )
* Add `sameSite` to Cookies metadata ( #134)

## What's Changed

* chore: add sameSite attribute to the http only cookie by @smakosh in <https://github.com/yezz123/authx/pull/134>
* docs: add smakosh as a contributor for code, security by @allcontributors in <https://github.com/yezz123/authx/pull/138>
* chore: update Requirements ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/139>
* CI: Add Code Security Analyse ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/140>
* empty Scheduled daily dependency update on Tuesday by @pyup-bot in <https://github.com/yezz123/authx/pull/141>
* chore: Add JWT Algorithm Choices ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/143>
* Docs: Add financial Supporters ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/144>
* Bump PyJWT version from 1.7.1 to 2.3.0 by @MojixCoder in <https://github.com/yezz123/authx/pull/151>
* docs: add MojixCoder as a contributor for code, bug by @allcontributors in <https://github.com/yezz123/authx/pull/152>
* chore: Remove Todos assign 🖇 by @yezz123 in <https://github.com/yezz123/authx/pull/153>
* Upgrade `pre-commit` requirements ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/154>

## New Contributors

* @smakosh made their first contribution in <https://github.com/yezz123/authx/pull/134>
* @MojixCoder made their first contribution in <https://github.com/yezz123/authx/pull/151>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.2...0.1.3>

## 0.1.2

After this discussion #124 with [@stephane](https://github.com/stephane) we need to change the package name that what pep's rules provide.

> Modules should have short, all-lowercase names. Underscores can be used in the module name if it improves readability. Python packages should also have short, all-lowercase names, although the use of underscores is discouraged.

![carbon](https://user-images.githubusercontent.com/52716203/140792904-39a9ddfa-c91b-4aa4-8069-955e38bf22a0.png)

## What's Changed

* Bump mkdocs-material from 7.2.6 to 7.3.5 by @dependabot in <https://github.com/yezz123/authx/pull/101>
* Docs: Prepare Project for Being Public ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/102>
* Bump mkdocs-material from 7.3.5 to 7.3.6 by @dependabot in <https://github.com/yezz123/authx/pull/103>
* Bump python from 3.9.2 to 3.10.0 by @dependabot in <https://github.com/yezz123/authx/pull/104>
* docs: add yezz123 as a contributor for code, doc, maintenance, infra by @allcontributors in <https://github.com/yezz123/authx/pull/105>
* docs: add AbderrahimSoubaiElidrissi as a contributor for review, doc by @allcontributors in <https://github.com/yezz123/authx/pull/106>
* CI: Delete Docs Build ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/108>
* Docs: Delete a part of FAQ ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/109>
* chore: Fix workflows ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/112>
* chore: Rename Website name & Fix Build Issue 🚀 by @yezz123 in <https://github.com/yezz123/authx/pull/113>
* Chore: Delete `aiohttp`  by @yezz123 in <https://github.com/yezz123/authx/pull/114>
* WIP: Add Code owner 🖇 by @yezz123 in <https://github.com/yezz123/authx/pull/117>
* Chore: Fix Key Directory 🔑  by @yezz123 in <https://github.com/yezz123/authx/pull/115>
* Configure `.pyup` ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/120>
* pep-0008: Fix Package and Module Names✨ by @yezz123 in <https://github.com/yezz123/authx/pull/126>
* chore: Change project Name by @yezz123 in <https://github.com/yezz123/authx/pull/128>
* chore: fix dockerfile commands by @yezz123 in <https://github.com/yezz123/authx/pull/130>
* Chore: change Name from `AuthX` to `authx` ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/131>
* Bump version from 0.1.1 to 0.1.2 ✨ by @yezz123 in <https://github.com/yezz123/authx/pull/132>

## New Contributors

* @allcontributors made their first contribution in <https://github.com/yezz123/authx/pull/105>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.1...0.1.2>

## 0.1.1

* Kuddos to [@AbderrahimSoubaiElidrissi](https://github.com/AbderrahimSoubaiElidrissi) for fixing multiple issues in docs ✨
* Fix Database partial router.
* Now we can call the `cache` or `mongo` only from a partial router.

### Example

<img width="654" alt="main py" src="https://user-images.githubusercontent.com/52716203/138797035-549804e4-0609-46aa-ba2f-e1b1f8757f59.png">

## What's Changed

* Add a partial router to Database ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/97>
* Docs: Update documentation by @yezz123 in <https://github.com/yezz123/AuthX/pull/98>
* Bump from 0.1.0 to 0.1.1 ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/99>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.1.0...0.1.1>

## 0.1.0

* Provide a full support for python 3.10 after adding a testcase (workflow), and fix the version of pytest.
* Provide a full requirements for `Setup.py` with all the dependencies and classifiers.

## What's Changed

* docs: Add All Contributor by @yezz123 in <https://github.com/yezz123/AuthX/pull/89>
* 📃 Docs: Add Codacy Review ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/90>
* CI: Fix Workflows ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/92>
* chore: Provide all requirements relate to `Setup.py` ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/93>
* ⬆️ Bump from 0.0.9 to 0.1.0 by @yezz123 in <https://github.com/yezz123/AuthX/pull/94>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.9...0.1.0>

## 0.0.9

* Add Code coverage and local testing for AuthenticationX.
* Add DocString to Some Functions relate to `Services`.
* Bump multiple packages to last release.

### What's Changed

* Bump mkdocs from 1.2.2 to 1.2.3 by @dependabot in <https://github.com/yezz123/AuthX/pull/78>
* Bump pytest-asyncio from 0.14.0 to 0.16.0 by @dependabot in <https://github.com/yezz123/AuthX/pull/77>
* 🐳 DockerFile Checker ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/80>
* chore: Provide DocString for Functions ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/84>
* Docs: Create a Release Notes ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/85>
* Chore: Add Local Testing & Code Coverage ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/86>
* Docs: Add Coverage Badge ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/87>
* ⬆️ Bump Version from 0.0.8 to 0.0.9 by @yezz123 in <https://github.com/yezz123/AuthX/pull/88>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.8...0.0.9>

## 0.0.8

### What's Changed

* Fix Highlighting Issue ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/69>
* Docs: Add some Typo ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/70>
* Add Code of Conducts & License ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/71>
* Switch to MIT License ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/73>
* Test Documentation Build ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/74>
* ⬆️ Bump from 0.0.7 to 0.0.8 ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/75>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.7...0.0.8>

## 0.0.7

### What's Changed

* Implement DocStrings ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/60>
* Create a Global Documentation using Mkdocs by @yezz123 in <https://github.com/yezz123/AuthX/pull/63>
* Fix Requirements by @yezz123 in <https://github.com/yezz123/AuthX/pull/66>
* Fix Documentation by @yezz123 in <https://github.com/yezz123/AuthX/pull/67>
* Version 0.0.7 ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/68>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.6...0.0.7>

## 0.0.6

### What's Changed

* Fix Environment Files by @yezz123 in <https://github.com/yezz123/AuthX/pull/54>
* Provide More Classifiers ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/57>
* Setup Tests DocStrings ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/58>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.5...0.0.6>

## 0.0.5

All this is based on This PR #45 :

* here I fix issues related to documentation.
* Generate a docstring for the main file.

### What's Changed

* ✨: Fix Documentation issue by @yezz123 in <https://github.com/yezz123/AuthX/pull/45>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.4...0.0.5>

## 0.0.4

During the work on this PR #44 :

* I generate a docstring to improve the project & clear some parts of the code.
* Add an Issue Template (Pre-public).
* Create a simple Readme For the whole users.
* Adding New Commands relate to the bumpversion package in the Makefile.

### What's Changed

* Setup docstring & Create Documentation by @yezz123 in <https://github.com/yezz123/AuthX/pull/44>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.3...0.0.4>

## 0.0.3

* Create a simple Readme.
* Create a Build to release the package.
* Fix Test Issues

### What's Changed

* Test : All functions in the Services and Fix some issues related to Raise() by @yezz123 in <https://github.com/yezz123/AuthX/pull/23>
* Release the first Version of AuthX ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/28>
* Create a Simple Readme by @yezz123 in <https://github.com/yezz123/AuthX/pull/42>
* Create 0.0.3 version by @yezz123 in <https://github.com/yezz123/AuthX/pull/43>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.2...0.0.3>

## 0.0.2

Create a Testable Core for Email and work on Users and JWT.
work on a PR to test the Services and Provide more Routers tests

### What's Changed

* Create a test for Email ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/25>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.1...0.0.2>

## 0.0.1

* Create Authentication Routes ex. Register, login, logout, and Reset.
* Add The Social Authentication Routes, Connecting using Google and Facebook.
* Give the Admin the Permission of Adding a User to the Blacklist or Ban a User from The API.
* Done with Setup of Multiple Routes and Fix The Crud Issues.
* Use the JWT package For Creating tokens and checking, also the Email Provider works with booths aiosmtplib and email-validator.
* Provide the Common Models ex. Users Models and Social Models.
* Create a Multiple Errors Support for Route and Models Validation or also if the Social Authentication CallBack got Errors.
* Add A Recaptcha Bypass using Httpx Library and Create A String and Signature Generator using Passlib.
* Using passlib to Verify the Password and Hash it under sha256.
* Set up a workflow to Test The Project in a Docker environment.

### What's Changed

* chore : Create Package Core by @yezz123 in <https://github.com/yezz123/AuthX/pull/1>
* chore: Provide The Full Functionality of Routers and Services by @yezz123 in <https://github.com/yezz123/AuthX/pull/2>
* chore: Create the Package Main file by @yezz123 in <https://github.com/yezz123/AuthX/pull/3>
* chore: Add Testing and Building Configuration by @yezz123 in <https://github.com/yezz123/AuthX/pull/5>
* chore: Add Last Build Addons to Test Branch by @yezz123 in <https://github.com/yezz123/AuthX/pull/8>
* chore: Create Dev work for testing the Package by @yezz123 in <https://github.com/yezz123/AuthX/pull/4>
* chore: Fix Build Files by @yezz123 in <https://github.com/yezz123/AuthX/pull/10>
* Isort AuthX path and Fix Missing packages for test by @yezz123 in <https://github.com/yezz123/AuthX/pull/18>
* adding test case to workflow by @yezz123 in <https://github.com/yezz123/AuthX/pull/19>

**Full Changelog**: <https://github.com/yezz123/AuthX/commits/0.0.1>
