# frozen_string_literal: true

class StudyQuery
  def self.default_study
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
      SELECT * FROM study_statuses WHERE name = 'Mask Recommender Based on Facial Features'
        SQL
      ).to_json
    )
  end
end
