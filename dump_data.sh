#!/usr/bin/env bash

echo "📦 Dumping data from MySQL..."

python manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes \
  --indent 2 \
  > Football_data.json

echo "✅ Data exported to Football_data.json"

python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 --settings=my_project.settings.local > Football_data.json
echo "✅ Data exported to Football_data.json"