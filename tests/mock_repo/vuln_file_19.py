```ruby
class User
  attr_accessor :name
  def initialize(name)
    @name = name
  end
end

def create_user(name)
  User.new(name)
end

input = "system('rm -rf *')"

# Unsafe use of 'eval'
eval("create_user('#{input}')")
```