class EmailSender
  def self.progress(dry_run: false)
    progresses = ParticipantProgress.call(manager_id: 1)
    still_participating = progresses.select{|p| !p['removed_from_study'] && p['manager_email'] }

    email_with_managed_users_data = still_participating.reduce({}) do |accum, p|
      unless accum.key?(p['manager_email'])
        accum[p['manager_email']] = []
      end

      accum[p['manager_email']] << p
      accum
    end

    email_with_managed_users_data.each do |email, progresses|
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
