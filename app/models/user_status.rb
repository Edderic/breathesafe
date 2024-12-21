class UserStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    results = UserStatusBuilder.build

    results.each do |email, details|
      UserStatus.create(
        uuid: email,
        high_risk: details['high_risk'],
        first_name: details['first_name'],
        last_name: details['last_name'],
        address_uuid: details['address_uuid'],
        refresh_datetime: datetime
      )

    end
  end
end
