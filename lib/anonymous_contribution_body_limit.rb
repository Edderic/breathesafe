# frozen_string_literal: true

require 'stringio'

# Bound the request before Rails parses JSON, and avoid oversized-body logging.
class AnonymousContributionBodyLimit
  LIMIT = 262_144

  def initialize(app)
    @app = app
  end

  def call(env)
    return @app.call(env) unless env['PATH_INFO'] == '/anonymous_contributions' && env['REQUEST_METHOD'] == 'POST'
    return reject(415) unless env['CONTENT_TYPE'].to_s.split(';').first == 'application/json'
    return reject(413) if env['CONTENT_LENGTH'].to_i > LIMIT

    input = env['rack.input']
    body = input.read(LIMIT + 1)
    return reject(413) if body.bytesize > LIMIT

    env['rack.input'] = StringIO.new(body)
    @app.call(env)
  end

  private

  def reject(status)
    headers = { 'Content-Type' => 'application/json', 'Cache-Control' => 'no-store' }
    [status, headers, ['{"error":"Unsupported or oversized contribution"}']]
  end
end
