class Status
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    ActiveRecord::Base.transaction do
      UserStatus.refresh!(datetime: datetime)
      StudyStatus.refresh!(datetime: datetime)
      StudyParticipantStatus.refresh!(datetime: datetime)

      TapeMeasureStatus.refresh!(datetime: datetime)
      DigitalCaliperStatus.refresh!(datetime: datetime)
      FacialMeasurementKitStatus.refresh!(datetime: datetime)

      MaskKitStatus.refresh!(datetime: datetime)

      HoodStatus.refresh!(datetime: datetime)
      NebulizerStatus.refresh!(datetime: datetime)
      SolutionStatus.refresh!(datetime: datetime)
      QualitativeFitTestingKitStatus.refresh!(datetime: datetime)

      AddressStatus.refresh!(datetime: datetime)

      ShippingStatus.refresh!(datetime: datetime)
    end
  end

  def self.destroy!
    UserStatus.destroy_all
    StudyStatus.destroy_all
    StudyParticipantStatus.destroy_all

    TapeMeasureStatus.destroy_all
    DigitalCaliperStatus.destroy_all
    FacialMeasurementKitStatus.destroy_all

    MaskKitStatus.destroy_all

    HoodStatus.destroy_all
    NebulizerStatus.destroy_all
    SolutionStatus.destroy_all
    QualitativeFitTestingKitStatus.destroy_all

    AddressStatus.destroy_all

    ShippingStatus.destroy_all
    ShippingStatusJoin.destroy_all
  end
end
