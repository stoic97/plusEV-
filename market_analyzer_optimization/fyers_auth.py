import os
import webbrowser
import time
import logging
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FyersAuth")

# Load environment variables or use defaults
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {str(e)}")

# Fyers credentials
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID', 'GBJMHA44CH-100')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY', 'YW543H05CG')
REDIRECT_URI = "https://www.google.com/"

def authenticate_fyers():
    """
    Complete Fyers authentication process and return access token.
    This function guides the user through the authentication flow in real-time.
    """
    logger.info("Starting Fyers authentication process...")
    
    # Step 1: Create session model
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type='code',
        grant_type='authorization_code'
    )
    
    # Step 2: Generate authorization URL and open browser immediately
    logger.info("Generating auth URL and opening browser...")
    auth_url = session.generate_authcode()
    print("\n" + "="*50)
    print("IMPORTANT INSTRUCTIONS:")
    print("1. A browser window will open for Fyers login")
    print("2. Complete the login process quickly")
    print("3. After being redirected to Google, immediately copy the ENTIRE URL")
    print("4. Paste the URL back here within 60 seconds")
    print("="*50 + "\n")
    
    # Open browser automatically
    webbrowser.open(auth_url)
    print(f"If the browser didn't open automatically, visit:\n{auth_url}\n")
    
    # Step 3: Prompt for redirect URL and extract auth code immediately
    redirect_url = input("After logging in, paste the complete redirect URL here: ")
    
    if "auth_code=" not in redirect_url:
        logger.error("No auth code found in the URL")
        return None
    
    auth_code = redirect_url.split("auth_code=")[1].split("&")[0]
    logger.info(f"Auth code extracted: {auth_code[:10]}...")
    
    # Step 4: Immediately set token and generate access token
    logger.info("Setting auth code and generating token...")
    session.set_token(auth_code)
    
    # Generate token
    response = session.generate_token()
    
    if "access_token" in response:
        access_token = response["access_token"]
        logger.info(f"Access token generated: {access_token[:10]}...")
        
        # Save token to file
        with open("fyers_token.txt", "w") as f:
            f.write(access_token)
        logger.info("Token saved to fyers_token.txt")
        
        return access_token
    else:
        logger.error(f"Failed to generate token: {response}")
        return None

def test_token(access_token):
    """Test if the token is valid by fetching profile information"""
    logger.info("Testing token validity...")
    
    fyers = fyersModel.FyersModel(
        client_id=FYERS_CLIENT_ID,
        token=access_token,
        is_async=False,
        log_path=os.getcwd()
    )
    
    try:
        profile = fyers.get_profile()
        if 's' in profile and profile['s'] == 'ok':
            logger.info("Token is valid!")
            logger.info(f"Connected as: {profile['data'].get('name', 'Unknown')}")
            return True
        else:
            logger.error(f"Token validation failed: {profile}")
            return False
    except Exception as e:
        logger.error(f"Error testing token: {str(e)}")
        return False

if __name__ == "__main__":
    # Try to authenticate with Fyers
    token = authenticate_fyers()
    
    if token:
        # Test if the token works
        test_token(token)
        
        print("\nNext steps:")
        print("1. Use this token in your crude data notebook")
        print("2. The token is also saved to fyers_token.txt")
        print("3. The token is valid for one day")
    else:
        print("\nAuthentication failed. Here are some troubleshooting tips:")
        print("1. Make sure your client ID and secret key are correct")
        print("2. Complete the login process quickly (within 60 seconds)")
        print("3. Copy the ENTIRE redirect URL, including 'https://www.google.com/?auth_code=...'")
        print("4. If you keep getting 'auth code expired', try clearing your browser cache or using incognito mode")