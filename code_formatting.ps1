echo "Running isort..."
isort src/

echo "Running black..."
black src/

echo "Running flake8..."
flake8 src/