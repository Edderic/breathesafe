Rails.application.routes.draw do
  devise_for :users, {
    registrations: 'registrations',
    sessions: 'users/sessions'
  }

  root to: 'events#new'

  devise_scope :user do
    get 'registrations/is_signed_in', to: 'registrations#is_signed_in'
    post 'users/log_in', to: 'users/sessions#create'
    delete 'users/log_out', to: 'users/sessions#destroy'
    get 'users/get_current_user', to: 'users/sessions#get_current_user'
  end

  post 'events', to: 'events#create'
  get 'events', to: 'events#index'
  get 'profiles', to: 'users/profiles#index'

  post 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#create_or_update'
  get 'users/:user_id/carbon_dioxide_monitors', to: 'users/carbon_dioxide_monitors#index'
  delete 'users/:user_id/carbon_dioxide_monitors/:carbon_dioxide_monitor_id', to: 'users/carbon_dioxide_monitors#delete'
  post 'users/:user_id/profiles', to: 'users/profiles#create_or_update'




  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  # root "articles#index"
end
