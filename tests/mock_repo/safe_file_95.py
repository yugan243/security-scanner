```ruby
class User < ActiveRecord::Base
  # Whitelist attributes for mass assignment
  attr_accessible :name, :email, :password, :admin

  # Strong parameters for mass assignment
  def user_params
    params.require(:user).permit(:name, :email, :password, :admin)
  end
end

# Create an instance of the User class using the parameters from the 'params[:user]' hash
user = User.new(user_params)
```