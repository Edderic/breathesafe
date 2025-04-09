require 'nokogiri'

class UspsOrderParser
  def initialize(filepath:)
    @file = File.open(filepath, 'r')
  end

  def parse_orders
    doc = Nokogiri::HTML.parse(@file)
    headers = doc.css("table thead tr").first.css('th')[2..].map(&:text)

    doc.css("table tbody tr").map do |row|
      date = row.css("td")[2].text
      name = row.css("td")[3].css("p").text
      address_array = row.css("td")[3].css("address")[0].children.map(&:text)
      address = address_array.reduce("") do |accum, item|
        unless item == ""
          accum += "\n" + item
        end

        accum
      end.lstrip.rstrip

      weight_oz = row.css("td")[5].children[0].text
      value = UspsOrderParser.get_value(row).text.split(": ")[1]
      label_number = row.css("td")[7].css('p').text


      {
        date: date,
        name: name,
        address: address,
        weight_oz: weight_oz,
        value: value,
        label_number: label_number
      }.with_indifferent_access
    end
  end

  class << self
    def get_value(row)
      row.css("td")[5].children.find{|c| c.text.match("Value") }
    end
  end
end
