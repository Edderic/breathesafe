# frozen_string_literal: true

class CommunityFitTesting
  class << self
    def generate_anonymized_users_for_email(email:, num_users:)
      manager = User.find_by(email: email)

      arr = []
      num_users.times do
        first_name = SecureRandom.uuid
        last_name = ''
        password = SecureRandom.uuid

        email = "#{first_name}@fake.com"
        ActiveRecord::Base.transaction do
          user = User.new(
            email: email,
            password: SecureRandom.uuid
          )

          user.skip_confirmation!
          user.save!

          Profile.create!(
            user_id: user.id,
            first_name: first_name,
            last_name: last_name,
            measurement_system: 'imperial'
          )

          ManagedUser.create!(
            manager_id: manager.id,
            managed_id: user.id
          )
        end

        arr << {
          email: email,
          first_name: first_name,
          last_name: last_name,
          password: password
        }
      end

      arr
    end
  end
end
