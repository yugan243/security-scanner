```ruby
class UserController < ApplicationController
  def show
    @user = User.find(params[:id])
    eval("@#{params[:method]}")
  end
end
```