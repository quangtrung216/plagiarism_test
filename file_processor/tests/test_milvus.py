from pymilvus import (
    connections,
    utility,
    Collection
)


# ================= CONFIG =================
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
DB_NAME = "plagiarism_db"
COLLECTION_NAME = "reference_vectors"
DIM = 768
# ==========================================


def connect_milvus():
    print("🔌 Connecting to Milvus...")

    connections.connect(
        alias="default",
        host=MILVUS_HOST,
        port=MILVUS_PORT,
        db_name=DB_NAME
    )

    print("✅ Connected to Milvus")
    print(f"📌 Database: {DB_NAME}\n")


def check_collection():
    print("📂 Checking collection...")

    if not utility.has_collection(COLLECTION_NAME):
        print(f"❌ Collection '{COLLECTION_NAME}' not found")
        return None

    print(f"✅ Found collection: {COLLECTION_NAME}\n")

    return Collection(COLLECTION_NAME)


def print_schema(collection: Collection):
    print("📐 Schema Info")
    print("-" * 40)

    schema = collection.schema

    print("AutoID:", schema.auto_id)

    for field in schema.fields:
        print(
            f"- {field.name}"
            f" | Type: {field.dtype}"
            f" | Primary: {field.is_primary}"
            f" | AutoID: {field.auto_id}"
        )

    print("-" * 40 + "\n")


def test_insert(collection: Collection):
    print("🧪 Testing insert...")

    # Fake vector
    vector = [0.01] * DIM

    try:
        res = collection.insert([vector])

        ids = res.primary_keys

        print("✅ Insert OK")
        print("Generated IDs:", ids)

    except Exception as e:
        print("❌ Insert failed")
        print("Error:", e)

    print()


def main():
    connect_milvus()

    collection = check_collection()
    if collection is None:
        return

    collection.load()

    print_schema(collection)

    indexes = collection.indexes

    if not collection.indexes:
        print("❌ No index found!")
    else:
        for idx in collection.indexes:
            print("Index Name :", idx.index_name)
            print("Field Name :", idx.field_name)
            print("Index Type :", idx.params.get("index_type"))
            print("Metric     :", idx.params.get("metric_type"))
            print("Params     :", idx.params)
            print("-" * 40)



if __name__ == "__main__":
    main()
