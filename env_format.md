# .env file format

```bash
GOOGLE_API_KEY="<google_api_key>"
SUPABASE_URL="<supabase_url>"
SUPABASE_KEY="<supabase_key>"
GOOGLE_CSE_ID="<google_cse_key>"
```
Replace the "content" with actual api_keys and urls, also make sure the .env file is mentioned in ".gitignore" file
- google_api_key is found over [here](https://aistudio.google.com/app/apikey)
- google_cse_id is found over [here](https://programmablesearchengine.google.com/controlpanel/all)
- supabase_url can be created over [here](https://supabase.com/dashboard/organizations)
- for supabase_key,
    - go to the project that you will use
    - go to project settings
    - go to API keys
    - use the key at "service role" section
    - Note: You might need special permission to get the API key if you are not the project owner.