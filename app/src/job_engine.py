import os
import logging
import aiohttp

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
LINKEDIN_HOST = "linkedin-job-search-api.p.rapidapi.com"

async def search_jobs(role: str, location: str = "United States") -> str:
    """
    Search for jobs using the LinkedIn Job Search API via RapidAPI (Async).
    """
    if not RAPIDAPI_KEY:
        return "⚠️ Error: RAPIDAPI_KEY is missing. Please configure it."

    url = f"https://{LINKEDIN_HOST}/search"
    
    querystring = {
        "query": f"{role} in {location}",
        "page": "1",
        "num_pages": "1",
        "date_posted": "any_time"
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": LINKEDIN_HOST
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=querystring) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"API Error {response.status}: {text}")
                    return f"❌ API Error: {response.status}"
                
                data = await response.json()
        
        # Adjust parsing based on actual API response structure
        # Assuming typical response list
        jobs = data if isinstance(data, list) else data.get("data", [])
        jobs = jobs[:5]
        
        if not jobs:
            return f"No jobs found for *{role}* in *{location}*."

        result = f"🔍 **Found Jobs for {role} in {location}:**\n\n"
        for job in jobs:
            title = job.get("job_title", "Unknown Role")
            company = job.get("company_name", "Unknown Company")
            link = job.get("job_url", "#")
            result += f"🔹 [{title}]({link}) at *{company}*\n"
            
        return result
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return f"❌ Failed to fetch jobs: {str(e)}"
