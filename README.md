# ShortenUrl

# set up the project
1. create the  /App folder in /home/{UserNmae}/App
2. cd to App and git clone xxx.git
3. run cmd: docker-compose up -d

# Test the Api under Linux:
test for Shorten Url:

curl -X POST -H "Content-Type: application/json" -d '{"original_url": "http://example.com"}' http://localhost:8000/api/createShortUrl


test for payload exceeds 2048:
curl -X POST -H "Content-Type: application/json" -d "{\"original_url\": \"$(printf 'A%.os' {1..2050})\"}" http://localhost:8000/api/createShortUrl


test for URL format error:
curl -X POST -H "Content-Type: application/json" -d '{"original_url": "example.com"}' http://localhost:8000/api/createShortUrl
   
