build:
	# Build the backend
	npm run scss
	python ./manage.py collectstatic --no-input
run:
	python ./manage.py runserver 0.0.0.0:8300 --settings=ghostz_cdl.settings.development
makemigrations:
	python ./manage.py makemigrations --settings=ghostz_cdl.settings.development
migrate:
	python ./manage.py migrate --settings=ghostz_cdl.settings.development