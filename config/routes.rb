

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

  post 'events/external/:api_token', to: 'events#external_create'

  post 'events', to: 'events#create'
  post 'events/:id/approve', to: 'events#approve'
  put 'events/:id', to: 'events#update'
  get 'events', to: 'events#index'
  get 'profiles', to: 'users/profiles#index'

  post 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#create_or_update'
  get 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#index'
  delete 'users/:user_id/carbon_dioxide_monitors/:carbon_dioxide_monitor_id', to: 'users/carbon_dioxide_monitors#delete'
  get 'users/:user_id/profile', to: 'users/profiles#show'
  post 'users/:user_id/profile', to: 'users/profiles#create'
  put 'users/:user_id/profile', to: 'users/profiles#update'

  get 'users/:user_id/facial_measurements', to: 'users/facial_measurements#show'
  post 'users/:user_id/facial_measurements', to: 'users/facial_measurements#create'

  get 'masks', to: 'masks#index'
  post 'masks', to: 'masks#create'
  get 'masks/:id', to: 'masks#show'
  put 'masks/:id', to: 'masks#update'
  delete 'masks/:id', to: 'masks#delete'

  get 'fit_tests', to: 'fit_tests#index'
  post 'fit_tests', to: 'fit_tests#create'
  get 'fit_tests/:id', to: 'fit_tests#show'
  put 'fit_tests/:id', to: 'fit_tests#update'
  delete 'fit_tests/:id', to: 'fit_tests#delete'

  post 'managed_users',to: 'managed_users#create'
  get 'managed_users',to: 'managed_users#index'
  get 'managed_users/:id',to: 'managed_users#show'
  delete 'managed_users/:id',to: 'managed_users#delete'

  post 'measurement_devices',to: 'measurement_devices#create'
  get 'measurement_devices',to: 'measurement_devices#index'
  get 'measurement_devices/:id',to: 'measurement_devices#show'
  put 'measurement_devices/:id',to: 'measurement_devices#update'
  delete 'measurement_devices/:id',to: 'measurement_devices#delete'

  post 'facial_measurements/:facial_measurement_id/fit_tests', to: 'facial_measurements_fit_tests#create'

  delete 'mask_kit/:managed_user_id/:mask_id/',to: 'mask_kit#delete'
  get 'mask_kit/:managed_user_id',to: 'mask_kit#index'

  controller :pages do
    get :qr_code_generator
    get :qr_code_download
  end


  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  # root "articles#index"
end


