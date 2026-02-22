```ruby
require 'mysql2'

def generate_query(user_input)
  client = Mysql2::Client.new(:host => "localhost", :username => "root", :password => "password")
  user_input = client.escape(user_input)
  "SELECT * FROM users WHERE username='#{user_input}'"
end

def login(username, password)
  query = generate_query(username)
  # Execute the query
  # Assume this function executes the SQL query safely
end

login("user", "password")
```