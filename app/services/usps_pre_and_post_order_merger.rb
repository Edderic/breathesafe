# frozen_string_literal: true

class UspsPreAndPostOrderMerger
  class << self
    def call(pre_order:, post_order:)
      collection = []
      pre_order.each do |to_create_row|
        post_order.each do |order|
          to_create_row_name = "#{to_create_row['Recipient First Name']} #{to_create_row['Recipient Last Name']}"
          next unless order['name'] == to_create_row_name

          # "order" should be in the argument of merge so that label_number
          # of the "order" overwrites the to_create_row one.
          collection << to_create_row.merge(order)
        end
      end

      collection
    end
  end
end
