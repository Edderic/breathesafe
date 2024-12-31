class AppError < StandardError
end

class UnrecognizedActionError < AppError
end

class UnsuccessfulScrapeError < AppError
  def initialize(msg="This is a custom exception", exception_type="custom")
    @exception_type = exception_type
    super(msg)
  end
end

