Shell Deployment Trigger Script 

export GEMINI_API_KEY="your_actual_api_key_here"

gcloud run deploy open-job-listings \
    --source . \
    --region us-central1 \
    --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY \
    --allow-unauthenticated
