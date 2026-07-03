To deploy this exact repository directly from GitHub to Google Cloud Run (leveraging Google's fully automated continuous deployment pipeline), follow these production setup steps.

This method ensures that every time you push a code change to your GitHub main branch, Google Cloud will automatically build the container and update your live Streamlit site.

Step 1: Push Your Local Files to GitHub
Make sure your file structure exactly matches your layout before linking to Google Cloud:

Bash
git init
git add .
git commit -m "feat: initial xprize submission sprint codebase"
git branch -M main
# Link and push to your private or public GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/open-job-listings.git
git push -u origin main
⚠️ Critical Hackathon Reminder: Go to your GitHub repository settings right now and invite testing@devpost.com and judging@hacker.fund as collaborators to fulfill your Day 1 compliance requirement.

Step 2: Enable the Required Google Cloud APIs
Open your Google Cloud Console terminal (Cloud Shell) or your local terminal authenticated with gcloud, and activate the services needed to execute the container-to-service pipeline:

Bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com
Step 3: Connect GitHub to Google Cloud Run
Instead of manually building Docker containers locally, we will use the Google Cloud Console graphical user interface to link GitHub directly.

Go to the Cloud Run page in the Google Cloud Console.

Click CREATE SERVICE.

Select "Continuously deploy new revisions from a source repository".

Click SET UP WITH CLOUD BUILD.

Select GitHub as your Repository Provider.

Authenticate your GitHub account and select your open-job-listings repository from the dropdown menu. Click Next.

Set your branch filter to ^main$ and select Dockerfile as your Build Configuration type. Leave the source path as /Dockerfile. Click Save.

Step 4: Configure Port, Hardware, and Secret API Keys
Before finalizing the deployment page, scroll down to expand the Advanced Settings configurations:

1. Networking Port Configuration
Go to the Container tab.

Change the Container Port field to exactly 8080 (this maps directly to the port exposed in your project Dockerfile).

2. Injecting the Gemini API Key Securely
Look for the Environment Variables or Secrets section.

Click ADD VARIABLE.

Set the Name to exactly: GEMINI_API_KEY

Set the Value to your live Google AI Studio / Vertex AI API key token string.

3. Execution Scaling & Invocation
Under Autoscaling, set the Minimum number of instances to 0 (This forces the Scale-to-Zero architecture so you do not incur charges while waiting for grading).

Under Authentication, select "Allow unauthenticated invocations" so that the general public and the hackathon judging committee can access your URL without signing into a Google IAM profile.

Step 5: Execute Deployment and Track URL
Click CREATE at the bottom of the Cloud Run configuration page.

Google Cloud Build will immediately grab the Dockerfile and python files from GitHub, compile them inside the Google Artifact Registry, and push the build active onto the serverless infrastructure.

Within 2 to 3 minutes, a green checkmark will appear next to your service name, and Google will provide a live, production HTTPS URL at the top of the pane (e.g., https://open-job-listings-xxxxxx.a.run.app).

Test your application live on the web by interacting with the sidebar support agent to confirm that your agent_execution_logs.json audit loops track correctly inside the live production container instance!
