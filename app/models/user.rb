class User < ApplicationRecord
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :lockable, :timeoutable, :trackable


  has_one :profile
  has_many :events, foreign_key: 'author_id'
  has_many :masks, foreign_key: 'author_id'
  has_many :facial_measurements, foreign_key: 'author_id'

  def carbon_dioxide_monitors
    CarbonDioxideMonitor.find_by_sql("select c.* from carbon_dioxide_monitors as c inner join user_carbon_dioxide_monitors as uc on (c.serial = uc.serial) where uc.user_id = #{self.id}")
  end

  def manages?(other_user)
    if self.admin
      true
    elsif self.id == other_user.id
      true
    elsif ManagedUser.for_manager_and_managed(
      manager_id: self.id,
      managed_id: other_user.id
    ).size > 0
      true
    else
      false
    end
  end

  def apply_study_datetimes(start_datetime:nil, goal_end_datetime: nil)
    if start_datetime.nil?
      start_datetime = DateTime.now
    end

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
end
