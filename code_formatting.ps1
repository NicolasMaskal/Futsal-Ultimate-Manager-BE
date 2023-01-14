echo "Running isort..."
isort src/ config/

echo "Running black..."
black src/ config/

echo "Running flake8..."
flake8 src/ config/

echo "Running mypy..."
mypy --config mypy.ini src/