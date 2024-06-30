import requests
from fastapi import HTTPException


def check_profanity(text: str) -> (bool, str):
    try:
        url = "https://www.purgomalum.com/service/containsprofanity"
        params = {"text": text}
        response = requests.get(url, params=params)

        if response.text.strip().lower() == "true":
            return True, "Content contains profanity or inappropriate language."

        return False, "Content is clean."

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to PurgoMalum API: {str(e)}"
        )
