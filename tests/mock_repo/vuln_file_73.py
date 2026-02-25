```ruby
class User
  attr_accessor :username, :password

  def initialize(username, password)
    @username = username
    @password = password
  end
end

user = User.new('test_user', 'test_password')

log_message = "User #{user.username} logged in with password #{user.password}"

puts log_message
```