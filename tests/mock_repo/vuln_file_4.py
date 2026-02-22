```ruby
def generate_query(user_input)
  "SELECT * FROM users WHERE username='#{user_input}'"
end

def login(username, password)
  query = generate_query(username)
  # Execute the query
  # Assume this function executes the SQL query safely
end

login("user", "password")
```