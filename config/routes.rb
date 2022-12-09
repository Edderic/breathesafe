

Rails.application.routes.draw do
  devise_for :users, controllers: {
    registrations: 'registrations',
    sessions: 'users/sessions',
    confirmations: 'users/confirmations'
  }

  root to: 'events#new'

  devise_scope :user do
    get 'registrations/is_signed_in', to: 'registrations#is_signed_in'
    post 'users/log_in', to: 'users/sessions#create'
    delete 'users/log_out', to: 'users/sessions#destroy'
    get 'users/get_current_user', to: 'users/sessions#get_current_user'
  end

  post 'events', to: 'events#create'
  post 'events/:id/approve', to: 'events#approve'
  get 'events', to: 'events#index'
  get 'profiles', to: 'users/profiles#index'

  post 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#create_or_update'
  get 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#index'
  delete 'users/:user_id/carbon_dioxide_monitors/:carbon_dioxide_monitor_id', to: 'users/carbon_dioxide_monitors#delete'
  get 'users/:user_id/profile', to: 'users/profiles#show'
  post 'users/:user_id/profile', to: 'users/profiles#create'
  put 'users/:user_id/profile', to: 'users/profiles#update'

  controller :pages do
    get :qr_code_generator
    get :qr_code_download
  end


  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  # root "articles#index"
end


