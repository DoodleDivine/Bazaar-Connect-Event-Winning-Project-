**This branch houses the backend of the project.**

Everything required to be in in backend (data saves, security/privacy) are all handled here.

I'll be explaining what the files do (if you read the Main.py file,
there are notes left over on different pieces of logic programs).

**Main.py**🔧🔐
- This is where all the core backend instructions happen (use of python).
- **Flask** was used to help host and maintain the website backend
AND with the use of HTTP requests, entered data by the user was pulled
and stored into its proper json file.
- Bcrypt was used to validate logic and keep credentials secure.
- Other libraries/packages were used as shortcuts to make work quicker.

**JSON files**🗃️
- These files were used for storing website data (as seen by the names of the files).
- At first, the intention was to use an actual database such as MongoDB or SQL using
Microsoft's SQL extension to link the saved data on there, but due to time this was
an improvision.
- When data was collected from **script.js**, **Main.py**'s Flask Framework
quickly stored the data temporarily and saved it to the actual data storage
intended (which are the json files).
