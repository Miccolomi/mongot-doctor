import os
import certifi
from pymongo import MongoClient
import traceback

uri = os.environ.get("MONGO_URI", "mongodb://mdb-admin:michele@work0.mongodb.pov.local:28014,work1.mongodb.pov.local:28014,work2.mongodb.pov.local:28014/?replicaSet=my-replica-set&tls=false")
print(f"Connecting to: {uri[:40]}...")

try:
    client = MongoClient(uri, tlsCAFile=certifi.where() if "tls=true" in uri.lower() else None, serverSelectionTimeoutMS=5000)
    db_names = [d for d in client.list_database_names() if d not in ("admin", "local", "config")]
    for db_name in db_names:
        db = client[db_name]
        for coll_name in db.list_collection_names():
            try:
                indexes = list(db[coll_name].list_search_indexes())
                if indexes:
                    print(f"\n--- {db_name}.{coll_name} ---")
                    for idx in indexes:
                        print(idx)
                        
                        try:
                            stats = db.command({"aggregate": coll_name, "pipeline": [{"$searchMeta": {"index": idx["name"], "exists": {"path": {"wildcard": "*"}}}}]})
                            print(f"Stats aggregate: {stats}")
                        except Exception as e:
                            print(f"SearchMeta count err: {e}")
            except Exception as e:
                pass
except Exception as e:
    traceback.print_exc()
