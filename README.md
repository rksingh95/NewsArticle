# NewsArticle
# rsingh95/newsarticle_web (Docker Image)

NOTE: In our case the user is created for admin login via conslole and is admin user creation
needs to take place via admin and so is the address. 

For django admin login
username-admin
password-admin

Url that can be used via postman are:

1.a. To get the   list of news articles that include only the headline 
   127.0.0.1:8000/blog/news/articles/
   GET METHOD:
   Example json: [
    {
        "id": "723f4b20-857a-449c-b73e-26cbc9e59513",
        "headline": "Coronavirus Lockdown"
    },
    {
        "id": "1bde5a99-1140-4023-993a-3ec51ff5435f",
        "headline": "Coronavirus Lockdown V2"
    }
]

1.b. To create the   list of news articles
   127.0.0.1:8000/blog/news/articles/
   POST METHOD:
   Input Json Example:  {
           "headline": "Coronavirus Lockdown ",
           "content": "Detail content of articel",
           "published": true,
           "author_id":"17f204e1-bbae-4e6d-9fd1-fffaeeee296b",
            }
   Response JSON post success :
         {
             "article_id": "36b0209c-0378-4447-a991-65ca9a176d2e"
         }
   Similar headlines cant be used: 400 Bad request with below error message

   {
    "headline": [
        "news article with this headline already exists."
    ]
}
   
2. returns details of a news article (headline & content) for a given id*
127.0.0.1:8000/blog/news/articles/pk/
   here pk is the given id 
   example url : 127.0.0.1:8000/blog/news/articles/723f4b20-857a-449c-b73e-26cbc9e59513/
   GET METHOD with UUID: 
   Example json:
            [{
             "id": "723f4b20-857a-449c-b73e-26cbc9e59513",
             "headline": "Coronavirus Lockdown",
             "content": "Detail content of articel",
             "author_email": "test@test.org",
             "author_id": "17f204e1-bbae-4e6d-9fd1-fffaeeee296b",
             "category_title": "Coronavirus Lockdown",
             "updated_at": "2021-01-20T20:26:16.387621Z"
         }]
   
3. 127.0.0.1:8000/blog/news/articles/content/ return all the articel with details as for the above returns only one article
   but this route returns all the article
   
   GET METHOD to access all the articels present:
   Example Json:
   [
    {
        "id": "723f4b20-857a-449c-b73e-26cbc9e59513",
        "headline": "Coronavirus Lockdown",
        "content": "Detail content of articel",
        "author_email": "test@test.org",
        "author_id": "17f204e1-bbae-4e6d-9fd1-fffaeeee296b",
        "categories": "Coronavirus Lockdown",
        "updated_at": "2021-01-20T20:26:16.387621Z"
    },
    {
        "id": "1bde5a99-1140-4023-993a-3ec51ff5435f",
        "headline": "Coronavirus Lockdown V2",
        "content": "Detail content of articel",
        "author_email": "test@test.org",
        "author_id": "17f204e1-bbae-4e6d-9fd1-fffaeeee296b",
        "categories": "Coronavirus Lockdown V2",
        "updated_at": "2021-01-20T20:02:42.465979Z"
    }
]
   
4. User list 127.0.0.1:8000/blog/users/ returns all the user present 



To access admin we use user as admin and password as admin.

Database used is postgresSql and all credential is in settings.py file.

To run the project migration is required and after that run the server then create user via admin
whereas news article get and create method can be checked via postman its all verified and working.



