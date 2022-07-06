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


  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  # root "articles#index"
end
