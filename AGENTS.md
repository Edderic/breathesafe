# Repository Guidelines

## Project Structure & Module Organization
- `app/` contains Rails MVC, mailers, jobs, services, and Vue frontend code in `app/javascript`.
- `config/` and `db/` hold Rails configuration, migrations, and schema.
- `spec/` is the primary test suite (models, services, controllers, system specs).
- `public/` and `app/assets/` store static assets; `coveragejs/` is Jest coverage output.
- `python/` houses data science notebooks and recommender tooling; `lambda/` packages AWS Lambda artifacts; `infra/` contains Terraform.
- `scripts/` provides local helpers (for example `scripts/run_lambda_locally.sh`).

## Build, Test, and Development Commands
- `bundle install` and `yarn install`: install Ruby and JS dependencies.
- `rails s`: run the Rails server locally.
- `./bin/vite dev`: run the Vite dev server for Vue assets.
- `rails db:create` / `rails db:migrate`: create and migrate the local database.
- `bundle exec rspec`: run the Ruby test suite.
- `bundle exec rubocop`: run Ruby linting used in CI.
- `npx jest`: run JS tests (configured in `package.json`).
- `cd python && poetry run pytest`: run Python tests for the recommender tooling.

## Coding Style & Naming Conventions
- Ruby style is governed by RuboCop settings in `.rubocop.yml`; follow existing conventions in nearby files.
- RSpec tests live in `spec/` and follow the `*_spec.rb` naming pattern.
- Vue components and JS modules live under `app/javascript`; keep naming consistent with existing component files.

## Testing Guidelines
- RSpec is the primary Rails test framework; specs are organized by type under `spec/`.
- Jest is configured for frontend tests and writes coverage to `coveragejs/`.
- Python tests use pytest (see `python/pyproject.toml`).
- CI runs RuboCop, RSpec, and Python test suites before deployment (see `DEPLOYMENT.md`).

## Commit & Pull Request Guidelines
- Recent commit messages are short, plain-English phrases (for example `improve masks ui`, `rubocop`).
- Open PRs against the `development` branch and include a brief summary plus test notes; tests must pass before merging.
- Deployment to staging/production is automated from `development` once checks succeed (see `DEPLOYMENT.md`).

## Configuration & Secrets
- Local environment variables are loaded via `.env` (git-ignored) and `~/.zshrc` sourcing `.breathesafe-zshrc`.
- Ask a maintainer for AWS credentials before running S3 or Lambda workflows.
