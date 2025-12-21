# frozen_string_literal: true

class User < ApplicationRecord
  acts_as_paranoid

  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :lockable, :timeoutable, :trackable

  # Prevent deleted users from logging in
  def active_for_authentication?
    super && !deleted?
  end

  # Custom message for deleted accounts
  def inactive_message
    deleted? ? :deleted_account : super
  end

  # Validate consent_form_version_accepted if present (legacy field)
  validate :consent_form_version_accepted_format, if: -> { consent_form_version_accepted.present? }

  # Helper methods for forms jsonb field
  def form_accepted?(form_name)
    forms.dig(form_name.to_s, 'version_accepted').present?
  end

  def form_version_accepted(form_name)
    forms.dig(form_name.to_s, 'version_accepted')
  end

  def form_accepted_at(form_name)
    accepted_at_str = forms.dig(form_name.to_s, 'accepted_at')
    Time.zone.parse(accepted_at_str) if accepted_at_str.present?
  rescue ArgumentError
    nil
  end

  def accept_form(form_name, version)
    self.forms ||= {}
    self.forms[form_name.to_s] = {
      'version_accepted' => version,
      'accepted_at' => Time.current.utc.iso8601
    }
  end

  def needs_to_accept_forms?(current_versions)
    return [] unless forms.is_a?(Hash)

    outdated_forms = []
    current_versions.each do |form_name, current_version|
      accepted_version = form_version_accepted(form_name)
      outdated_forms << form_name.to_s if accepted_version.nil? || accepted_version != current_version
    end
    outdated_forms
  end

  has_one :profile, dependent: :destroy, inverse_of: :user
  has_many :masks, foreign_key: 'author_id', inverse_of: :user # rubocop:disable Rails/HasManyOrHasOneDependent
  has_many :facial_measurements, dependent: :destroy, inverse_of: :user
  has_many :bulk_fit_tests_imports, dependent: :destroy

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

  # Soft delete user account - anonymizes PII while keeping consent records
  def soft_delete!
    transaction do
      # Delete all managed users where this user is the manager
      ManagedUser.where(manager_id: id).find_each do |mu|
        managed_user = User.find_by(id: mu.managed_id)
        next unless managed_user

        # Delete the managed user's data
        managed_user.soft_delete_user_data!
      end

      # Delete this user's data
      soft_delete_user_data!

      # Anonymize email and unconfirmed_email, then mark as deleted
      anonymized_email = "deleted_user_#{SecureRandom.uuid}@example.invalid"
      update!(
        email: anonymized_email,
        unconfirmed_email: nil,
        deleted_at: Time.current
      )
    end
  end

  # Helper method to delete user data (used by soft_delete! for both manager and managed users)
  def soft_delete_user_data!
    # Delete profile
    profile&.destroy

    # Delete facial measurements and related fit tests
    facial_measurements.each do |fm|
      FitTest.where(facial_measurement_id: fm.id).destroy_all
      fm.destroy
    end

    # Delete bulk fit test imports
    bulk_fit_tests_imports.destroy_all

    # Delete managed user relationships
    ManagedUser.where(managed_id: id).destroy_all
  end
end
