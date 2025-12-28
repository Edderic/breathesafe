web: bundle exec puma -C config/puma.rb
python_service: cd python/mask_component_predictor && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 app:app
release: bundle exec rails db:migrate && bundle exec rails mask_predictor:train
