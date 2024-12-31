class AppError < StandardError
end

class UnrecognizedActionError < AppError
end

class UnsuccessfulScrapeError < AppError
end

