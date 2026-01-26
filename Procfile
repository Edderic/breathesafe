web: bundle exec puma -C config/puma.rb
worker: bundle exec sidekiq -C config/sidekiq.yml
python_service: cd python/mask_component_predictor && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 app:app
release: bash bin/release.sh
