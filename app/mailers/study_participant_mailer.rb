class StudyParticipantMailer < ApplicationMailer
  default from: 'info@breathesafe.xyz', bcc: 'info@breathesafe.xyz'

  def shipping_label_assigned
    @user = params[:user]
    @shipping_label = params[:shipping_label]

    mail(to: @user['email'], subject: "Mask Recommender: Shipping Label created")
  end
end
