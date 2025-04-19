from ast import Mult
from app.backend.agents.rate import RateAgent
from app.backend.store.db import Pool
from app.backend.store import Store
from app.backend.llm import MultiModalLLM
from app.backend.models.ad import Ad

db_pool = Pool(
    host="localhost",
    port=5432,
    dbname="app",
    user="postgres",
    password="postgres",
)
store = Store(db_pool)

llm = MultiModalLLM(model="gemini-2.5-flash-preview-04-17")

agent = RateAgent(llm, store)

personalities = store.personality.list_all()
print([p.to_dict() for p in personalities])
personality = store.personality.get("2bb7508a-cee1-494d-b1d3-6e4bd92f5f5d")

if not personality:
    print("Personality not found")
    exit(1)

ad = None
ads = store.ad.list_all()
if ads:
    ad = ads[0]
else:
    print("No ads found")
    print("Making one")
    ad = Ad(
        image="ad1.jpg",
    )
    store.ad.create(ad)
    
    print("Ad created:", ad)

print("Rating ad...")

result = agent(personality.id, ad.id)

print("DONE")
print(result.to_dict())