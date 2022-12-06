class User < ApplicationRecord
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :confirmable, :lockable, :timeoutable, :trackable


  has_one :profile

  def carbon_dioxide_monitors
    CarbonDioxideMonitor.find_by_sql("select c.* from carbon_dioxide_monitors as c inner join user_carbon_dioxide_monitors as uc on (c.serial = uc.serial) where uc.user_id = #{self.id}")
  end
end
