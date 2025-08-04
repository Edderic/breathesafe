# frozen_string_literal: true

class EmailSender
  def self.progress(manager_id:, dry_run: false)
    progresses = ParticipantProgress.call(manager_id: manager_id)
    still_participating = progresses.select do |p|
      !p['removed_from_study'] && !p['finished_study'] && p['manager_email']
    end

    email_with_managed_users_data = still_participating.each_with_object({}) do |p, accum|
      accum[p['manager_email']] = [] unless accum.key?(p['manager_email'])

      accum[p['manager_email']] << p
    end

    filter_out_fully_complete_pods = email_with_managed_users_data.select do |_email, progresses|
      progresses.any? do |p|
        (p['demog_percent_complete'].to_f < 100.0) ||
          (p['fm_percent_complete'].to_f < 100.0) ||
          (p['fit_testing_percent_complete'].to_f >= 100.0)
      end
    end

    filter_out_fully_complete_pods.each do |email, progresses|
      to_email = if dry_run
                   'info@breathesafe.xyz'
                 else
                   email
                 end

      StudyParticipantMailer.with(
        to_email: to_email,
        progresses: progresses
      ).progress.deliver_now
    end
  end
end
