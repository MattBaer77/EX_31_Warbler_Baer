### Step Seven: Research and Understand Login Strategy
Look over the code in app.py related to authentication.

Questions:

- How is the logged in user being kept track of?
    - The logged in user's ID is being tracked by Flask's session object.
    - If an ID exists in the session object, that ID is being used to query the database model for the user with that ID before every request.
    - If no ID exists in the session object, the value of g.user is set to NONE, and logic within the routes ensure that the user is redirected to the apporpriate routes for that use case.
<br>
<br>
- What is Flask’s g object?
    - The Flask g object is an object which stores data during a request. It does not store data between requests. it is used to manage resources during the request.
<br>
<br>
- What is the purpose of add_user_to_g?
    - The user is added to g so that the properties of the user object with the ID stored in session can be referenced, compared, and manipulated.
<br>
<br>
- What does @app.before_request mean?
    - Functions and variables defined within @app.before_request decorator are declared before and can be used within each route.
<br>
<br>