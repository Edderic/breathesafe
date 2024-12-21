Geocoder.configure(
  timeout: 10,

  # set default units to kilometers:
  units: :miles

  # caching (see Caching section below for details):
  # cache: Redis.new,
  # cache_options: {
    # expiration: 1.day, # Defaults to `nil`
    # prefix: "another_key:" # Defaults to `geocoder:`
  # }
)
