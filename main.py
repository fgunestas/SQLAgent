from components.agent_pipeline import agent_pipeline
import os
import urllib.request

if __name__ == "__main__":

    if not os.path.exists("chinook.db"):
        url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
        urllib.request.urlretrieve(url, "chinook.db")
        print("chinook.db indirildi.")
    else:
        print("chinook.db zaten var.")
    from sqlalchemy import create_engine, text

    engine = create_engine("sqlite:///chinook.db")


    try:
        with engine.connect() as conn:
            result = conn.execute("select * from playlists").fetchall()
        print(result)
    except Exception as e:
        print(str(e))

    user_query = input("Soru: ")
    response = agent_pipeline(user_query,test=1)
    print("\nYanıt:\n", response)