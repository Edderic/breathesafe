class AddressQuery
  def self.find_address_of(user_email: nil)
    if user_email.nil?
      user_email = 'edderic@gmail.com'
    end

    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
      SELECT * FROM user_statuses
      INNER JOIN address_statuses ON address_statuses.uuid = user_statuses.address_uuid
      WHERE user_statuses.uuid = '#{user_email}'
        SQL
      ).to_json
    )
  end
end
