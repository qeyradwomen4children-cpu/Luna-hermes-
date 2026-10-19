# Luna + Hermes Agent setup

This is a separate integration starter for Luna and Hermes. It does not rename or modify your existing `Luna` repository.

## Included
- `AGENTS.md` — repository-level working rules for agents
- `hermes_skills/luna-core/SKILL.md` — Luna's operating principles and workflow
- `docs/DEPLOYMENT_CHECKLIST.md` — staged setup and verification checklist
- `.github/workflows/required-files.yml` — GitHub Actions check for required files

## Install on GitHub (Android)
1. Create a new, separate repository named `luna-hermes`. Leave your existing `Luna` repository unchanged.
2. In the new repository, choose **Add file → Upload files** (or the `+` menu, depending on the app version).
3. Extract this ZIP first if GitHub's mobile app won't preserve folder paths. Use your phone's browser and desktop-site option if needed.
4. Upload the files while preserving the paths shown in this ZIP, then commit them to the default branch.
5. Open **Actions** and confirm the `Required files` workflow passes.

## Important limitation
This package creates repository scaffolding only. It does not install Hermes on a server, connect credentials, or run an agent. Those steps require a selected runtime and explicit permissions.
