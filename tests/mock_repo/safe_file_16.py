```ruby
require 'pg'

def search_user(username)
  conn = PG.connect(dbname: 'test')
  conn.prepare('select_user', "SELECT * FROM users WHERE username = $1")
  res  = conn.exec_prepared('select_user', [username])
  res.each do |row|
    puts row
  end
ensure
  conn.close if conn
end

search_user("test' OR '1'='1")
```