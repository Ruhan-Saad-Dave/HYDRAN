# Features to implement 

1. AI Symptom Checker 
    1. Need to be RAG based
    2. Should refer to data to reply 
    3. If no data is found, attempt to perform websearch 
2. SMS Based Medicine Stock Retrieval 
    1. Update stock from clinic 
    2. Return stock details to users
    3. Reserve stock for user 
    4. Show clinic with the medicine
3. Offline Medical Records 
    1. Doctor can save the reports on server DB 
    2. Doctor can retrieve particular patient reports 
    3. When user device sends a request, server should find the difference and update the local DB 
4. Video Calling
    1. app will encode the video and audio frame.
    2. need to trasfer the encoded data to other side 
    3. maintain constant data flow 
5. Overall
    1. Build endpoints for all features
    2. Write Unit and Integration test
    3. Connect to Supabase
