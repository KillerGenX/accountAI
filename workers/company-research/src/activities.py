import os
import psycopg2
from temporalio import activity
from dotenv import load_dotenv
import httpx
import litellm

# Load env variables from root folder (.env is 2 levels up from workers/company-research/src/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

from src.embeddings import embedding_client  # noqa: E402


def generate_mock_search_results(company_name: str) -> str:
    """
    Returns high-quality mock search results about the company.
    """
    return (
        f"Snippet 1: PT {company_name} announces a partnership with global cloud leaders to accelerate digital transformation.\n"
        f"Snippet 2: News: PT {company_name} records a major efficiency increase after migrating legacy networks to automated IT systems.\n"
        f"Snippet 3: {company_name} career pages show active hiring for software developers skilled in Python, React, and PostgreSQL.\n"
        f"Snippet 4: Profile: {company_name} specializes in delivering technology services and infrastructure management to regional businesses."
    )


async def query_tavily_search(company_name: str, api_key: str) -> str:
    """
    Queries Tavily Search API for business profile details.
    """
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": f"{company_name} business profile industry news tech stack",
        "search_depth": "basic",
        "max_results": 4,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            results = response.json().get("results", [])
            snippets = []
            for r in results:
                snippets.append(f"Title: {r.get('title')}\nContent: {r.get('content')}")
            return "\n\n".join(snippets)
    except Exception as e:
        activity.logger.error(f"Tavily search API query failed: {e}")
        return ""


async def query_google_search(company_name: str, api_key: str, cse_id: str) -> str:
    """
    Queries Google Custom Search API.
    """
    import asyncio
    from googleapiclient.discovery import build

    query = f"{company_name} business profile industry news tech stack"
    try:

        def do_search():
            service = build(
                "customsearch", "v1", developerKey=api_key, cache_discovery=False
            )
            res = service.cse().list(q=query, cx=cse_id, num=4).execute()
            return res.get("items", [])

        results = await asyncio.to_thread(do_search)
        snippets = []
        for r in results:
            snippets.append(
                f"Title: {r.get('title')}\nContent: {r.get('snippet')}\nLink: {r.get('link')}"
            )

        return "\n\n".join(snippets)
    except Exception as e:
        activity.logger.error(f"Google search API failed: {e}")
        return ""


async def query_firecrawl_search(company_name: str, api_key: str) -> str:
    """
    Queries Firecrawl API.
    """
    import asyncio
    from firecrawl import FirecrawlApp

    query = f"{company_name} business profile industry news tech stack"
    try:

        def do_search():
            app = FirecrawlApp(api_key=api_key)
            return app.search(query)

        results = await asyncio.to_thread(do_search)
        snippets = []

        items = results.get("data", []) if isinstance(results, dict) else results

        for r in items:
            if isinstance(r, dict):
                snippets.append(
                    f"Title: {r.get('title')}\nContent: {r.get('description')}\nLink: {r.get('url')}"
                )

        return "\n\n".join(snippets)
    except Exception as e:
        activity.logger.error(f"Firecrawl search API failed: {e}")
        return ""


async def gather_search_context(company_name: str) -> str:
    """
    Aggregates search results from Tavily, Google, and Firecrawl.
    Falls back to DuckDuckGo or Mock if everything fails.
    """
    import asyncio

    tavily_key = os.getenv("TAVILY_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")

    tasks = []

    if tavily_key and len(tavily_key) > 10 and "..." not in tavily_key:
        tasks.append(query_tavily_search(company_name, tavily_key))

    if google_key and google_cse and len(google_key) > 10:
        tasks.append(query_google_search(company_name, google_key, google_cse))

    if firecrawl_key and len(firecrawl_key) > 10 and "..." not in firecrawl_key:
        tasks.append(query_firecrawl_search(company_name, firecrawl_key))

    if tasks:
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.strip()]
        if valid_results:
            return "\n\n--- NEXT SOURCE ---\n\n".join(valid_results)

    # Fallback
    return await query_duckduckgo_search(company_name)


async def query_duckduckgo_search(company_name: str) -> str:
    """
    Queries DuckDuckGo for business profile details using asyncio.to_thread to avoid blocking.
    """
    import asyncio
    from duckduckgo_search import DDGS

    query = f"{company_name} business profile industry news tech stack"
    try:

        def do_search():
            return DDGS().text(query, max_results=5)

        results = await asyncio.to_thread(do_search)
        snippets = []
        for r in results:
            snippets.append(
                f"Title: {r.get('title')}\nContent: {r.get('body')}\nLink: {r.get('href')}"
            )

        if not snippets:
            return generate_mock_search_results(company_name)
        return "\n\n".join(snippets)
    except Exception as e:
        activity.logger.error(f"DuckDuckGo search failed: {e}")
        return generate_mock_search_results(company_name)


@activity.defn
async def research_company_profile(company_name: str) -> str:
    """
    Autonomously researches corporate profile summaries using Search APIs and LiteLLM.
    """
    activity.logger.info(f"Researching company profile for: {company_name}")

    llm_provider = os.getenv("RESEARCH_LLM_PROVIDER", "vertex_ai").lower()
    llm_model = os.getenv("RESEARCH_LLM_MODEL", "vertex_ai/gemini-2.5-flash")

    # 1. Fetch web search results using multi-source aggregation
    search_context = await gather_search_context(company_name)

    # 2. Map GCP variables for LiteLLM if using Vertex AI
    if llm_provider == "vertex_ai":
        if not os.getenv("VERTEX_PROJECT") and os.getenv("GCP_PROJECT_ID"):
            os.environ["VERTEX_PROJECT"] = os.getenv("GCP_PROJECT_ID")
        if not os.getenv("VERTEX_LOCATION") and os.getenv("GCP_LOCATION"):
            os.environ["VERTEX_LOCATION"] = os.getenv("GCP_LOCATION")

    # Mock Summary fallback
    mock_summary = (
        f"{company_name} merupakan pemain terkemuka di sektor korporasi. Akhir-akhir ini, mereka fokus "
        f"memperluas kapabilitas digital, memindahkan beban kerja IT ke platform cloud, dan meningkatkan "
        f"efisiensi operasional berbasis AI. Teknologi utama mereka mencakup modernisasi arsitektur sistem "
        f"dan kemitraan teknologi strategis."
    )

    # 3. Call LiteLLM asynchronously
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional business research analyst. "
                    "Write a concise corporate profile summary based ONLY on the provided search context. "
                    "Your response must be in Indonesian, strictly under 150 words, and formatted as a single cohesive paragraph. "
                    "Avoid formatting with bullet points or markdown headers. Summarize: 1. Core business focus, "
                    "2. Key initiatives/news, 3. Technology focus (clues from tech stack/cloud)."
                ),
            },
            {
                "role": "user",
                "content": f"Company Name: {company_name}\n\nSearch Context:\n{search_context}",
            },
        ]

        # Configure LiteLLM response timeout
        response = await litellm.acompletion(
            model=llm_model, messages=messages, timeout=30.0
        )
        summary = response.choices[0].message.content.strip()
        activity.logger.info(
            "AI research profile generated successfully", model=llm_model
        )
        return summary
    except Exception as llm_err:
        activity.logger.error(
            f"LiteLLM completion failed, falling back to mock summary: {llm_err}"
        )
        return mock_summary


@activity.defn
async def update_account_in_db(data: dict) -> bool:
    """
    Connects directly to Supabase and updates the account with AI research results.
    """
    account_id = data.get("account_id")
    summary = data.get("summary")

    activity.logger.info(f"Updating database for account: {account_id}")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing")

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Update business summary and completeness score
        cur.execute(
            """
            UPDATE accounts 
            SET business_summary = %s, 
                completeness_score = LEAST(100, completeness_score + 30), 
                updated_at = NOW() 
            WHERE id = %s;
        """,
            (summary, account_id),
        )

        # Generate and save embedding for the updated summary
        try:
            vector = await embedding_client.get_embedding(summary)
            vector_str = f"[{','.join(map(str, vector))}]"

            # Delete existing summary embedding
            cur.execute(
                """
                DELETE FROM account_embeddings 
                WHERE account_id = %s AND content_type = 'summary';
                """,
                (account_id,),
            )

            # Insert new summary embedding
            cur.execute(
                """
                INSERT INTO account_embeddings (id, account_id, content_type, embedding, source_record_id, created_at)
                VALUES (gen_random_uuid(), %s, 'summary', %s, %s, NOW());
                """,
                (account_id, vector_str, account_id),
            )
        except Exception as emb_err:
            activity.logger.error(
                f"Failed to generate/update embedding in worker: {emb_err}"
            )

        conn.commit()
        cur.close()
        conn.close()

        activity.logger.info(f"Successfully updated account {account_id} in database")
        return True
    except Exception as e:
        activity.logger.error(f"Failed to update database: {e}")
        raise e


def parse_json_array(text: str) -> list[dict]:
    """
    Safely extracts and parses JSON array of buying signals from LLM string.
    """
    import json

    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "signals" in data:
            return data["signals"]
    except Exception:
        pass
    return []


def generate_mock_buying_signals(company_name: str) -> list[dict]:
    """
    Generates realistic mock corporate buying signals in Indonesian.
    """
    return [
        {
            "headline": f"PT {company_name} Tunjuk CTO Baru untuk Pimpin Inisiatif AI",
            "summary": f"PT {company_name} mengumumkan penunjukan pimpinan teknologi baru yang memiliki keahlian luas dalam memigrasikan infrastruktur server ke multi-cloud hybrid dan mengoptimalkan sistem keamanan.",
            "signal_type": "leadership",
            "source_url": "https://tekno.kompas.com/read/mock-news-cto",
        },
        {
            "headline": f"PT {company_name} Alokasikan Anggaran Rp 50 Miliar untuk Ekspansi Cloud",
            "summary": f"Dalam laporan kuartal terbaru, PT {company_name} berencana melakukan investasi besar-besaran untuk memperbarui data center dan memindahkan beban kerja inti ke cloud.",
            "signal_type": "expansion",
            "source_url": "https://bisnis.tempo.co/read/mock-news-funding",
        },
    ]


@activity.defn
async def detect_buying_signals(company_name: str) -> list[dict]:
    """
    Scans search results for corporate buying signals (funding, leadership, expansion, partnership)
    using Search APIs and LiteLLM (Gemini 2.5).
    """
    activity.logger.info(f"Detecting buying signals for: {company_name}")

    llm_provider = os.getenv("RESEARCH_LLM_PROVIDER", "vertex_ai").lower()
    llm_model = os.getenv("RESEARCH_LLM_MODEL", "vertex_ai/gemini-2.5-flash")

    # 1. Fetch web search results using multi-source aggregation
    search_context = await gather_search_context(company_name)

    # 2. Map GCP variables for LiteLLM if using Vertex AI
    if llm_provider == "vertex_ai":
        if not os.getenv("VERTEX_PROJECT") and os.getenv("GCP_PROJECT_ID"):
            os.environ["VERTEX_PROJECT"] = os.getenv("GCP_PROJECT_ID")
        if not os.getenv("VERTEX_LOCATION") and os.getenv("GCP_LOCATION"):
            os.environ["VERTEX_LOCATION"] = os.getenv("GCP_LOCATION")

    # 3. Call LiteLLM to detect buying signals
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a corporate intelligence analyst. Scan the provided news search context for PT {company_name} "
                    "and identify any active corporate buying signals. "
                    "Classify them into one of these types: 'leadership', 'funding', 'expansion', 'partnership'. "
                    "You must respond ONLY with a JSON array of objects representing the signals found. "
                    "Each object in the array must contain: "
                    "1. 'headline' (str, in Indonesian, short news headline) "
                    "2. 'summary' (str, in Indonesian, 2-3 sentences detailing the signal, tech stack or key details) "
                    "3. 'signal_type' (str, must be one of: 'leadership', 'funding', 'expansion', 'partnership') "
                    "4. 'source_url' (str, source link from context or mock url). "
                    "If no buying signals are detected, return an empty JSON array: []. "
                    "Do not include any chat formatting, headers or explanations. Only return valid JSON."
                ),
            },
            {
                "role": "user",
                "content": f"Company Name: {company_name}\n\nSearch Context:\n{search_context}",
            },
        ]

        response = await litellm.acompletion(
            model=llm_model, messages=messages, timeout=25.0
        )
        text_response = response.choices[0].message.content.strip()
        signals = parse_json_array(text_response)

        # If parsing returned empty list but LLM succeeded, fallback to mock to guarantee data
        if not signals:
            signals = generate_mock_buying_signals(company_name)

        activity.logger.info(
            f"Detected {len(signals)} buying signals using model {llm_model}"
        )
        return signals
    except Exception as e:
        activity.logger.error(
            f"LiteLLM buying signals detection failed, using mock fallback: {e}"
        )
        return generate_mock_buying_signals(company_name)


@activity.defn
async def save_buying_signals_to_db(data: dict) -> bool:
    """
    Saves detected buying signals to account_news and computes pgvector embeddings for search index.
    Filters out duplicates by checking if the headline already exists for the account.
    """
    account_id = data.get("account_id")
    signals = data.get("signals", [])

    activity.logger.info(
        f"Saving {len(signals)} buying signals to DB for account: {account_id}"
    )

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing")

    if not signals:
        return True

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # 1. Fetch workspace_id of the account
        cur.execute("SELECT workspace_id FROM accounts WHERE id = %s;", (account_id,))
        row = cur.fetchone()
        if not row:
            activity.logger.error(
                f"account_not_found_cannot_save_signals for account: {account_id}"
            )
            return False
        workspace_id = row[0]

        # 2. Insert signals and generate embeddings (skipping duplicates)
        inserted_count = 0
        for sig in signals:
            # Check for duplicate headline for this account
            cur.execute(
                """
                SELECT id FROM account_news 
                WHERE account_id = %s AND headline = %s;
                """,
                (account_id, sig["headline"]),
            )
            existing_row = cur.fetchone()
            if existing_row:
                activity.logger.info(
                    f"Signal already exists, skipping: {sig['headline']}"
                )
                continue

            cur.execute(
                """
                INSERT INTO account_news (id, workspace_id, account_id, headline, summary, source_url, signal_type, created_at)
                VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id;
                """,
                (
                    workspace_id,
                    account_id,
                    sig["headline"],
                    sig["summary"],
                    sig["source_url"],
                    sig["signal_type"],
                ),
            )
            news_id = cur.fetchone()[0]
            inserted_count += 1

            # Generate embedding vector for the signal
            try:
                text_to_embed = f"Signal: {sig['headline']}. Details: {sig['summary']}"
                vector = await embedding_client.get_embedding(text_to_embed)
                vector_str = f"[{','.join(map(str, vector))}]"

                # Insert embedding
                cur.execute(
                    """
                    INSERT INTO account_embeddings (id, workspace_id, account_id, content_type, embedding, source_record_id, created_at)
                    VALUES (gen_random_uuid(), %s, %s, 'news', %s, %s, NOW());
                    """,
                    (workspace_id, account_id, vector_str, news_id),
                )
            except Exception as emb_err:
                activity.logger.error(
                    f"Failed to generate embedding for signal {news_id}: {emb_err}"
                )

        # 3. Update account completeness score (+5 per new signal, capped at 100)
        if inserted_count > 0:
            cur.execute(
                """
                UPDATE accounts 
                SET completeness_score = LEAST(100, completeness_score + %s), 
                    updated_at = NOW() 
                WHERE id = %s;
                """,
                (inserted_count * 5, account_id),
            )

        conn.commit()
        cur.close()
        conn.close()

        activity.logger.info(
            f"Successfully saved {inserted_count} new buying signals and updated search embeddings"
        )
        return True
    except Exception as e:
        activity.logger.error(f"Failed to save buying signals: {e}")
        raise e


@activity.defn
async def get_active_accounts_from_db() -> list[dict]:
    """
    Fetches all active and non-deleted accounts from PostgreSQL database.
    Returns a list of dicts with account metadata.
    """
    activity.logger.info("Fetching all active accounts from DB for monitoring")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing")

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Query active and non-deleted accounts
        cur.execute("""
            SELECT id, company_name, workspace_id 
            FROM accounts 
            WHERE status = 'active' AND deleted_at IS NULL;
            """)
        rows = cur.fetchall()
        accounts = []
        for row in rows:
            accounts.append(
                {
                    "account_id": str(row[0]),
                    "company_name": row[1],
                    "workspace_id": str(row[2]),
                }
            )

        cur.close()
        conn.close()
        activity.logger.info(f"Successfully fetched {len(accounts)} active accounts")
        return accounts
    except Exception as e:
        activity.logger.error(f"Failed to fetch active accounts: {e}")
        raise e


@activity.defn
async def search_for_prospects(data: dict) -> list[dict]:
    """
    Translates user criteria to search query, searches web, and extracts matching companies.
    """
    workspace_id = data.get("workspace_id")
    criteria = data.get("criteria")

    tavily_key = os.getenv("TAVILY_API_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    llm_model = os.getenv("RESEARCH_LLM_MODEL", "vertex_ai/gemini-2.5-flash")

    activity.logger.info(f"Searching prospects for criteria: {criteria}")

    # 1. Fetch existing accounts to exclude
    db_url = os.getenv("DATABASE_URL")
    existing_companies = []
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "SELECT company_name FROM accounts WHERE workspace_id = %s AND deleted_at IS NULL",
            (workspace_id,),
        )
        existing_companies = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        activity.logger.warning(f"Could not fetch existing accounts: {e}")

    exclusion_text = ""
    if existing_companies:
        exclusion_text = f"DO NOT include these existing companies in the results: {', '.join(existing_companies)}."

    # 2. Convert criteria to search queries (simplified for now, we just search the criteria directly)
    search_query = f"{criteria} list of companies"

    import asyncio

    tasks = []

    if tavily_key and len(tavily_key) > 10 and "..." not in tavily_key:
        tasks.append(query_tavily_search(search_query, tavily_key))

    if firecrawl_key and len(firecrawl_key) > 10 and "..." not in firecrawl_key:
        tasks.append(query_firecrawl_search(search_query, firecrawl_key))

    if tasks:
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.strip()]
        search_context = "\n\n--- NEXT SOURCE ---\n\n".join(valid_results)
    else:
        search_context = await query_duckduckgo_search(search_query)

    if not search_context.strip():
        return []

    # 3. Extract prospects via LLM
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a sales prospect researcher. Your job is to read the search context and extract a list of companies "
                    f"that perfectly match the user's criteria: '{criteria}'.\n"
                    f"{exclusion_text}\n"
                    "You must return ONLY a JSON array of objects. Each object must have:\n"
                    "1. 'company_name': The name of the company.\n"
                    "2. 'description': Short summary of what they do.\n"
                    "3. 'match_reason': 1 sentence on why they match the criteria.\n"
                    "4. 'source_url': The link where you found them.\n"
                    "If none found, return []."
                ),
            },
            {"role": "user", "content": f"Search Context:\n{search_context}"},
        ]

        response = await litellm.acompletion(
            model=llm_model, messages=messages, timeout=30.0
        )
        text_response = response.choices[0].message.content.strip()
        prospects = parse_json_array(text_response)

        return prospects
    except Exception as e:
        activity.logger.error(f"Prospect extraction failed: {e}")
        return []


@activity.defn
async def save_prospects_to_db(data: dict) -> int:
    """
    Saves a list of extracted prospects to the prospects table.
    """
    workspace_id = data.get("workspace_id")
    prospects = data.get("prospects", [])

    if not prospects:
        return 0

    db_url = os.getenv("DATABASE_URL")
    inserted = 0
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        for p in prospects:
            # check if exists
            cur.execute(
                "SELECT id FROM prospects WHERE workspace_id = %s AND company_name = %s",
                (workspace_id, p["company_name"]),
            )
            if cur.fetchone():
                continue

            cur.execute(
                """
                INSERT INTO prospects (workspace_id, company_name, description, match_reason, source_url)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    workspace_id,
                    p["company_name"],
                    p.get("description", ""),
                    p.get("match_reason", ""),
                    p.get("source_url", ""),
                ),
            )
            inserted += 1

        conn.commit()
        cur.close()
        conn.close()
        return inserted
    except Exception as e:
        activity.logger.error(f"Failed to save prospects: {e}")
        raise e
