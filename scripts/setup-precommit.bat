@echo off

echo Installing pre-commit...
pip install pre-commit

echo Installing pre-commit hooks...
pre-commit install
pre-commit install --hook-type commit-msg

echo Installing frontend dependencies...
cd frontend
pnpm add -D prettier eslint-config-prettier

echo Pre-commit setup complete!