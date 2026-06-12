"""
INDB → Knowledge Graph Import Pipeline  (psycopg2, sync, batch reconnect)
==========================================================================
Run once from the backend directory:
    python scripts/import_indb.py

Idempotent — uses ON CONFLICT DO NOTHING everywhere.
Reconnects every BATCH_SIZE rows to survive Neon's connection timeout.
"""
import sys, os, time, uuid, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pandas as pd
import psycopg2

# ── Config ────────────────────────────────────────────────────────────────────
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
DB_URL_RAW   = os.environ.get("DATABASE_URL", "")
INDB_PATH    = Path(os.environ.get("INDB_FILE_PATH",
               ROOT / ".." / "data" / "Anuvaad_INDB_2024.11.xlsx"))
BATCH_SIZE   = 50      # reconnect every N rows
RATE_DELAY   = 0.12    # seconds between Gemini calls

SKIP_EMBEDDINGS = not GEMINI_KEY or GEMINI_KEY == "your-gemini-api-key-here"

# Convert SQLAlchemy URL → psycopg2 DSN
def _to_dsn(url: str) -> str:
    url = url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")
    # user:pass@host/db?...
    m = re.match(r"([^:]+):([^@]+)@([^/]+)/([^?]+)", url)
    if not m:
        raise ValueError(f"Cannot parse DATABASE_URL: {url}")
    user, pwd, host, db = m.groups()
    return f"host={host} dbname={db} user={user} password={pwd} sslmode=require"

DSN = _to_dsn(DB_URL_RAW)

# ── Gemini embedding (optional) ────────────────────────────────────────────────
if not SKIP_EMBEDDINGS:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)

def embed_text(text: str) -> list[float] | None:
    if SKIP_EMBEDDINGS:
        return None
    try:
        r = genai.embed_content(model="models/text-embedding-004",
                                content=text, task_type="retrieval_document")
        return r["embedding"]
    except Exception as e:
        print(f"      embed error: {e}")
        return None

def vec_str(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"

# ── Food knowledge helpers ────────────────────────────────────────────────────
from app.services.embeddings.food_embedding import (
    infer_category, infer_region, infer_meal_type,
    get_food_knowledge, build_food_embedding_text,
)

# ── Nutrient definitions ──────────────────────────────────────────────────────
NUTRIENT_DEFS = [
    ("energy_kcal","energy_kcal","kcal","energy"),
    ("energy_kj","energy_kj","kJ","energy"),
    ("carb_g","carb_g","g","macro"),
    ("protein_g","protein_g","g","macro"),
    ("fat_g","fat_g","g","macro"),
    ("freesugar_g","freesugar_g","g","macro"),
    ("fibre_g","fibre_g","g","macro"),
    ("cholesterol_mg","cholesterol_mg","mg","macro"),
    ("sfa_mg","sfa_mg","mg","macro"),
    ("mufa_mg","mufa_mg","mg","macro"),
    ("pufa_mg","pufa_mg","mg","macro"),
    ("calcium_mg","calcium_mg","mg","mineral"),
    ("phosphorus_mg","phosphorus_mg","mg","mineral"),
    ("magnesium_mg","magnesium_mg","mg","mineral"),
    ("sodium_mg","sodium_mg","mg","mineral"),
    ("potassium_mg","potassium_mg","mg","mineral"),
    ("iron_mg","iron_mg","mg","mineral"),
    ("copper_mg","copper_mg","mg","mineral"),
    ("zinc_mg","zinc_mg","mg","mineral"),
    ("selenium_ug","selenium_ug","μg","mineral"),
    ("manganese_mg","manganese_mg","mg","mineral"),
    ("vita_ug","vita_ug","μg","vitamin"),
    ("vite_mg","vite_mg","mg","vitamin"),
    ("vitd2_ug","vitd2_ug","μg","vitamin"),
    ("vitd3_ug","vitd3_ug","μg","vitamin"),
    ("vitk1_ug","vitk1_ug","μg","vitamin"),
    ("vitk2_ug","vitk2_ug","μg","vitamin"),
    ("folate_ug","folate_ug","μg","vitamin"),
    ("vitb1_mg","vitb1_mg","mg","vitamin"),
    ("vitb2_mg","vitb2_mg","mg","vitamin"),
    ("vitb3_mg","vitb3_mg","mg","vitamin"),
    ("vitb5_mg","vitb5_mg","mg","vitamin"),
    ("vitb6_mg","vitb6_mg","mg","vitamin"),
    ("vitb7_ug","vitb7_ug","μg","vitamin"),
    ("vitb9_ug","vitb9_ug","μg","vitamin"),
    ("vitc_mg","vitc_mg","mg","vitamin"),
    ("carotenoids_ug","carotenoids_ug","μg","vitamin"),
]

def _safe(val) -> float:
    try:
        f = float(val)
        return 0.0 if f != f else f
    except Exception:
        return 0.0

def new_conn():
    return psycopg2.connect(DSN, connect_timeout=30)

# ─────────────────────────────────────────────────────────────────────────────

def _exec_ddl(sql: str):
    """Run a single DDL statement on its own fresh connection+commit."""
    c = new_conn()
    try:
        with c.cursor() as cur:
            cur.execute(sql)
        c.commit()
    finally:
        c.close()


def setup_schema(_conn=None):  # _conn unused; kept for call-site compat
    """Create all tables. Each DDL gets its own connection to avoid pooler timeouts."""
    stmts = [
        "CREATE EXTENSION IF NOT EXISTS vector",
        """CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT)""",
        """CREATE TABLE IF NOT EXISTS regions (
            id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, country TEXT DEFAULT 'India')""",
        """CREATE TABLE IF NOT EXISTS meal_types (
            id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL)""",
        """CREATE TABLE IF NOT EXISTS foods (
            id TEXT PRIMARY KEY, indb_code TEXT UNIQUE,
            name TEXT NOT NULL, canonical_name TEXT NOT NULL,
            description TEXT,
            category_id  TEXT REFERENCES categories(id),
            region_id    TEXT REFERENCES regions(id),
            meal_type_id TEXT REFERENCES meal_types(id),
            embedding vector(768),
            created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ)""",
        """CREATE TABLE IF NOT EXISTS food_aliases (
            id TEXT PRIMARY KEY,
            food_id TEXT NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
            alias TEXT NOT NULL, language TEXT DEFAULT 'en',
            confidence REAL DEFAULT 1.0,
            UNIQUE(food_id, alias))""",
        """CREATE TABLE IF NOT EXISTS nutrients (
            id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL,
            unit TEXT NOT NULL, category TEXT, description TEXT)""",
        """CREATE TABLE IF NOT EXISTS food_nutrients (
            food_id     TEXT NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
            nutrient_id TEXT NOT NULL REFERENCES nutrients(id) ON DELETE CASCADE,
            value_per_100g REAL NOT NULL DEFAULT 0,
            PRIMARY KEY (food_id, nutrient_id))""",
        """CREATE TABLE IF NOT EXISTS ingredients (
            id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, embedding vector(768))""",
        """CREATE TABLE IF NOT EXISTS food_ingredients (
            food_id       TEXT NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
            ingredient_id TEXT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
            quantity_g REAL, is_primary TEXT DEFAULT 'true',
            PRIMARY KEY (food_id, ingredient_id))""",
        # NOTE: HNSW index created AFTER data load (see create_hnsw_index())
        """CREATE TABLE IF NOT EXISTS meals (
            id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
            image_url TEXT,
            detected_foods JSONB DEFAULT '[]',
            total_calories REAL DEFAULT 0, protein_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0, fat_g REAL DEFAULT 0, fiber_g REAL DEFAULT 0,
            micronutrients JSONB DEFAULT '{}', health_scores JSONB DEFAULT '{}',
            question_answers JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ)""",
        """CREATE TABLE IF NOT EXISTS analysis_sessions (
            id TEXT PRIMARY KEY, image_url TEXT,
            detected_foods JSONB DEFAULT '[]', questions JSONB DEFAULT '[]',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT now())""",
    ]
    for sql in stmts:
        _exec_ddl(sql)


def create_hnsw_index():
    """Create HNSW index after data is loaded (much faster post-load)."""
    _exec_ddl("""
        CREATE INDEX IF NOT EXISTS ix_foods_embedding_hnsw
        ON foods USING hnsw (embedding vector_cosine_ops)
        WITH (m=16, ef_construction=64)
    """)


def seed_lookups(conn):
    """Seed categories, regions, meal_types, nutrients. Return id maps."""
    CATS  = ["Breakfast","Rice","Bread","Curry","Snack","Beverage",
             "Sweet","Condiment","Other"]
    REGS  = ["Tamil Nadu","Karnataka","Andhra Pradesh","Telangana","Kerala",
             "Hyderabad","Punjab","Maharashtra","Gujarat","Rajasthan",
             "West Bengal","All India","North India","South India"]
    MEALS = ["Breakfast","Lunch","Dinner","Snack","Dessert"]

    cat_ids, reg_ids, meal_ids, nut_ids = {}, {}, {}, {}

    with conn.cursor() as cur:
        for name in CATS:
            cid = str(uuid.uuid4())
            cur.execute("INSERT INTO categories(id,name) VALUES(%s,%s) ON CONFLICT(name) DO NOTHING", (cid,name))
            cur.execute("SELECT id FROM categories WHERE name=%s", (name,))
            cat_ids[name] = cur.fetchone()[0]

        for name in REGS:
            rid = str(uuid.uuid4())
            cur.execute("INSERT INTO regions(id,name) VALUES(%s,%s) ON CONFLICT(name) DO NOTHING", (rid,name))
            cur.execute("SELECT id FROM regions WHERE name=%s", (name,))
            reg_ids[name] = cur.fetchone()[0]

        for name in MEALS:
            mid = str(uuid.uuid4())
            cur.execute("INSERT INTO meal_types(id,name) VALUES(%s,%s) ON CONFLICT(name) DO NOTHING", (mid,name))
            cur.execute("SELECT id FROM meal_types WHERE name=%s", (name,))
            meal_ids[name] = cur.fetchone()[0]

        for _col, name, unit, cat in NUTRIENT_DEFS:
            nid = str(uuid.uuid4())
            cur.execute("INSERT INTO nutrients(id,name,unit,category) VALUES(%s,%s,%s,%s) ON CONFLICT(name) DO NOTHING",
                        (nid,name,unit,cat))
            cur.execute("SELECT id FROM nutrients WHERE name=%s", (name,))
            row = cur.fetchone()
            if row:
                nut_ids[name] = row[0]

    conn.commit()
    return cat_ids, reg_ids, meal_ids, nut_ids


def import_batch(conn, batch: list[dict], cat_ids, reg_ids, meal_ids, nut_ids, ing_cache: dict):
    """Insert one batch of food rows within a single transaction."""
    with conn.cursor() as cur:
        for item in batch:
            food_code    = item["food_code"]
            food_name    = item["food_name"]
            category     = item["category"]
            region       = item["region"]
            meal_type    = item["meal_type"]
            aliases      = item["aliases"]
            ingredients  = item["ingredients"]
            description  = item["description"]
            embedding_v  = item["embedding"]
            nutrients_kv = item["nutrients"]

            food_id = str(uuid.uuid4())
            embed_arg = embedding_v  # None or formatted string

            cur.execute("""
                INSERT INTO foods(id,indb_code,name,canonical_name,description,
                    category_id,region_id,meal_type_id,embedding)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                ON CONFLICT(indb_code) DO NOTHING""",
                (food_id, food_code, food_name, food_name, description or None,
                 cat_ids.get(category), reg_ids.get(region), meal_ids.get(meal_type),
                 embed_arg))

            cur.execute("SELECT id FROM foods WHERE indb_code=%s", (food_code,))
            row = cur.fetchone()
            if not row:
                continue
            food_id = row[0]

            # Aliases
            for alias in aliases:
                cur.execute("""
                    INSERT INTO food_aliases(id,food_id,alias,confidence)
                    VALUES(%s,%s,%s,1.0) ON CONFLICT(food_id,alias) DO NOTHING""",
                    (str(uuid.uuid4()), food_id, alias.lower()))

            # Nutrients
            for nut_name, value in nutrients_kv.items():
                if nut_name not in nut_ids or value == 0.0:
                    continue
                cur.execute("""
                    INSERT INTO food_nutrients(food_id,nutrient_id,value_per_100g)
                    VALUES(%s,%s,%s)
                    ON CONFLICT(food_id,nutrient_id) DO UPDATE
                    SET value_per_100g=EXCLUDED.value_per_100g""",
                    (food_id, nut_ids[nut_name], value))

            # Ingredients
            for ing_name in ingredients:
                key = ing_name.lower().strip()
                if key not in ing_cache:
                    iid = str(uuid.uuid4())
                    cur.execute("INSERT INTO ingredients(id,name) VALUES(%s,%s) ON CONFLICT(name) DO NOTHING",
                                (iid, key))
                    cur.execute("SELECT id FROM ingredients WHERE name=%s", (key,))
                    ing_cache[key] = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO food_ingredients(food_id,ingredient_id,is_primary)
                    VALUES(%s,%s,'true') ON CONFLICT DO NOTHING""",
                    (food_id, ing_cache[key]))

    conn.commit()


def main():
    print("=" * 60)
    print("NutriLens India – INDB Knowledge Graph Import")
    print("=" * 60)
    if SKIP_EMBEDDINGS:
        print("  Mode: DATA ONLY (no embeddings — add GEMINI_API_KEY later)")
        print("  After adding key: python scripts/generate_embeddings.py")
    else:
        print("  Mode: FULL (data + Gemini embeddings)")
    print()

    # ── Schema ────────────────────────────────────────────────────────────────
    print("[1/5] Setting up schema…")
    setup_schema()
    print("      Schema ready.")

    # ── Lookups ───────────────────────────────────────────────────────────────
    print("[2/5] Seeding lookup tables…")
    conn = new_conn()
    cat_ids, reg_ids, meal_ids, nut_ids = seed_lookups(conn)
    print(f"      {len(cat_ids)} categories, {len(reg_ids)} regions, "
          f"{len(meal_ids)} meal types, {len(nut_ids)} nutrients.")

    # ── Load Excel ────────────────────────────────────────────────────────────
    print(f"[3/5] Loading {INDB_PATH.name}…")
    df = pd.read_excel(str(INDB_PATH), engine="openpyxl")
    print(f"      {len(df)} foods × {len(df.columns)} columns.")

    # ── Check already-imported ────────────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("SELECT indb_code FROM foods")
        already = {r[0] for r in cur.fetchall()}
    print(f"      {len(already)} foods already in DB.")

    # ── Build item list ───────────────────────────────────────────────────────
    print("[4/5] Processing rows…")
    items = []
    for _, row in df.iterrows():
        code = str(row.get("food_code", "")).strip()
        name = str(row.get("food_name", "")).strip()
        if not name or name.lower() == "nan" or code in already:
            continue

        nl = name.lower()
        cat  = infer_category(nl)
        reg  = infer_region(nl, cat)
        mt   = infer_meal_type(cat, nl)
        know = get_food_knowledge(nl)
        if know:
            cat = know.get("category", cat)
            reg = know.get("region", reg)
            mt  = know.get("meal_type", mt)

        aliases     = know.get("aliases", [])
        ingredients = know.get("ingredients", [])
        description = know.get("description", "")

        # Nutrients dict
        nutrients_kv = {}
        for _col, nut_name, _, _ in NUTRIENT_DEFS:
            if _col in df.columns:
                nutrients_kv[nut_name] = _safe(row.get(_col))

        # Embedding (only if key present)
        embedding_v = None
        if not SKIP_EMBEDDINGS:
            text = build_food_embedding_text(
                name=name, canonical_name=name,
                category=cat, region=reg, meal_type=mt,
                ingredients=ingredients, aliases=aliases, description=description,
            )
            embedding_v = embed_text(text)
            if embedding_v:
                embedding_v = vec_str(embedding_v)
            time.sleep(RATE_DELAY)

        items.append(dict(
            food_code=code, food_name=name,
            category=cat, region=reg, meal_type=mt,
            aliases=aliases, ingredients=ingredients,
            description=description, embedding=embedding_v,
            nutrients=nutrients_kv,
        ))

    print(f"      {len(items)} new foods to insert.")

    # ── Batch import ──────────────────────────────────────────────────────────
    print("[5/5] Inserting in batches…")
    ing_cache: dict = {}
    inserted = 0

    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start : start + BATCH_SIZE]
        # Fresh connection every batch to avoid Neon timeout
        try:
            conn.close()
        except Exception:
            pass
        conn = new_conn()

        import_batch(conn, batch, cat_ids, reg_ids, meal_ids, nut_ids, ing_cache)
        inserted += len(batch)
        print(f"      {inserted}/{len(items)} inserted…")

    try:
        conn.close()
    except Exception:
        pass

    print()
    print(f"Import complete: {inserted} foods, {len(ing_cache)} ingredients.")
    if inserted > 0:
        print("[+] Building HNSW index…")
        create_hnsw_index()
        print("    Index ready.")
    if SKIP_EMBEDDINGS:
        print()
        print("Next step — add your Gemini key to backend/.env, then run:")
        print("    python scripts/generate_embeddings.py")
        print("That fills in embeddings → enables semantic search.")
    print("=" * 60)


if __name__ == "__main__":
    main()
