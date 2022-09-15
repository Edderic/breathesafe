class PagesController < ApplicationController
    def qr_code_generator; end
  
    def qr_code_download
      send_data RQRCode::QRCode.new(params[:content].to_s).as_png(size: 300), type: 'image/png', disposition: 'attachment'
    end
  end