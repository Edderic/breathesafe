# frozen_string_literal: true

class User < ApplicationRecord
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :lockable, :timeoutable, :trackable

  # Validate consent_form_version_accepted if present
  validate :consent_form_version_accepted_format, if: -> { consent_form_version_accepted.present? }

  has_one :profile, dependent: :destroy, inverse_of: :user
  has_many :events, foreign_key: 'author_id', dependent: :destroy, inverse_of: :user
  has_many :masks, foreign_key: 'author_id', inverse_of: :user # rubocop:disable Rails/HasManyOrHasOneDependent
  has_many :facial_measurements, foreign_key: 'author_id', dependent: :destroy, inverse_of: :user

  def carbon_dioxide_monitors
    CarbonDioxideMonitor.find_by_sql(
      <<-SQL
      select c.* from carbon_dioxide_monitors
      as c inner join user_carbon_dioxide_monitors as uc on (c.serial = uc.serial) where uc.user_id = #{id}"
      SQL
    )
  end

  def manages?(other_user)
    if admin
      true
    elsif id == other_user.id
      true
    elsif ManagedUser.for_manager_and_managed(
      manager_id: id,
      managed_id: other_user.id
    ).size.positive?
      true
    else
      false
    end
  end

  def apply_study_datetimes(start_datetime: nil, goal_end_datetime: nil)
    start_datetime = DateTime.now if start_datetime.nil?

    profile = self.profile
    profile.update(
      study_start_datetime: start_datetime,
      study_goal_end_datetime: goal_end_datetime
    )

    # TODO: Assume that there is a MaskToUser table that tells us which masks
    # have not yet been tested by that user.
    #
    # Assign the current set of targeted masks to this user, along with
    # the managed users of this user.
    # If we don't do this and just assume that everyone has the same set of
    # targeted masks, it's simpler, but not flexible and could give wrong data
  end

  # Validation for consent_form_version_accepted
  def consent_form_version_accepted_format
    # Reject invalid values like "{}" or empty strings
    if consent_form_version_accepted == '{}' ||
       consent_form_version_accepted.blank? ||
       !consent_form_version_accepted.is_a?(String)
      errors.add(:consent_form_version_accepted, 'must be a valid version string')
    end
  end

  # Override Devise's notification sending to handle SMTP errors gracefully
  # This prevents user registration from failing if email delivery fails
  def send_devise_notification(notification, *args)
    super
  rescue ArgumentError => e
    # Handle SMTP configuration errors (e.g., missing API key)
    if e.message.include?('SMTP-AUTH') || e.message.include?('secret phrase')
      Rails.logger.error("Failed to send #{notification} email to #{email}: #{e.message}")
      # Don't re-raise - allow user registration to succeed even if email fails
      return
    end
    raise
  rescue StandardError => e
    # Log other email errors but don't fail registration
    Rails.logger.error("Failed to send #{notification} email to #{email}: #{e.class}: #{e.message}")
    Rails.logger.error(e.backtrace.join("\n")) if e.backtrace
    # Don't re-raise - allow user registration to succeed even if email fails
  end
end
