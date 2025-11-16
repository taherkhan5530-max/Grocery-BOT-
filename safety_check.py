import aiohttp
import config

async def check_image(image_path):
    """
    Checks an image against the Sight Engine API for explicit content.
    Returns True if explicit, False otherwise.
    """
    if not config.SE_API_USER or not config.SE_API_SECRET:
        print("Warning: Sight Engine API credentials not set. Skipping safety check.")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            data = {
                'models': 'nudity-2.0,wad', # Check for nudity, weapons, alcohol, drugs
                'api_user': config.SE_API_USER,
                'api_secret': config.SE_API_SECRET
            }
            
            with open(image_path, 'rb') as f:
                data['media'] = f.read()

                async with session.post('https://api.sightengine.com/1.0/check.json', data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Check nudity (e.g., raw score > 0.5)
                        if result.get('nudity', {}).get('raw', 0) > 0.5:
                            return True
                        # Check weapons/alcohol/drugs (any probability > 0.5)
                        if result.get('weapon', 0) > 0.5 or \
                           result.get('alcohol', 0) > 0.5 or \
                           result.get('drugs', 0) > 0.5:
                            return True
                            
                        return False
                    else:
                        print(f"Sight Engine Error: {await response.text()}")
                        return False # Fail safe: treat as non-explicit if API fails
    except Exception as e:
        print(f"Error in safety_check: {e}")
        return False # Fail safe
