# Backend for HYDRAN

## Steps to setup:
1. open git bash and type
```bash
git clone https://github.com/Ruhan-Saad-Dave/HYDRAN.git
```
2. open the folder "HYDRAN" in your editor, you can mostly find this file at C drive
3. open terminal in command prompt
4. If you do not have UV package installer, type:
```bash
pip install uv
```
5. After that type:
```bash
uv sync
```
This will download all the dependencies.
6. To run the file:
```bash
uv run main.py
```
7. If you want to install a new library:
```bash
uv add <library_name>
```

## Methods to commit:
1. make sure your code is error free and works with the code codes.
2. write some comments and documentation so that others can understand the file (just like this one)
3. use conventional messaging format for the commit message, eg:
```bash
Feat: Implemented endpoint for AI chatbot
```
4. If an error is found, put it on issue (putting and solving issue boosts your github profile)
5. If there is a file or folder that is not supposed to go on github (like API keys), put the file name in .gitignore file. 
6. If you have included a .env file, make sure to mention the variable names (not value) in the documentation.
