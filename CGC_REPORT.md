# CGC Report

_Generated: 2026-08-22 19:02 UTC_

_Scoped to repository: `/data/Desktop/nexus-clip`_


## God Nodes — Highest Fan-In
_These nodes are called from many places. High fan-in increases risk: a change here affects every caller._

| Kind | Name | File | In-degree |
| --- | --- | --- | --- |
| Function | get | tests/conftest.py | 18 |
| Function | showToast | contexts/BoardContext.tsx | 15 |
| Function | delete | tests/conftest.py | 9 |
| Function | __init__ | core/exceptions.py | 8 |
| Function | useBoard | contexts/BoardContext.tsx | 8 |
| Class | ClipService | services/clip_service.py | 6 |
| Function | create | repositories/user_repository.py | 5 |
| Function | get_by_id | repositories/user_repository.py | 5 |
| Function | fetchClips | contexts/BoardContext.tsx | 4 |
| Class | BoardService | services/board_service.py | 4 |
| Class | GuestService | services/guest_service.py | 4 |
| Function | fetchBoards | contexts/BoardContext.tsx | 4 |
| Function | get_or_create_session | services/guest_service.py | 4 |
| Function | get_redis_client | cache/redis.py | 4 |
| Function | create_access_token | auth/jwt.py | 3 |


## Most Complex Functions
_Cyclomatic complexity > 10 is a refactoring candidate._

| Function | File | Cyclomatic Complexity |
| --- | --- | --- |
| BoardProvider | contexts/BoardContext.tsx | 31 |
| QuickInput | components/QuickInput.tsx | 27 |
| ClipCard | components/ClipCard.tsx | 13 |
| detectType | components/QuickInput.tsx | 12 |
| SettingsDrawer | components/SettingsDrawer.tsx | 11 |
| fetchClips | contexts/BoardContext.tsx | 10 |
| handleSubmit | components/QuickInput.tsx | 9 |
| verify_google_id_token | auth/google.py | 7 |
| GuestContinueModal | components/GuestContinueModal.tsx | 7 |
| AuthModal | components/AuthModal.tsx | 7 |
| fetchBoards | contexts/BoardContext.tsx | 6 |
| deleteBoard | contexts/BoardContext.tsx | 6 |
| get | cache/cache_manager.py | 6 |
| normalize_url | services/metadata_service.py | 6 |
| verify_access_token | auth/jwt.py | 6 |


## Cross-Module Connections
_Calls that cross package boundaries — review for unexpected coupling._

| Caller | Caller File | Callee | Callee File | Confidence |
| --- | --- | --- | --- | --- |
| <module> | api/auth.py | get | tests/conftest.py | AMBIGUOUS |
| <module> | api/clips.py | get | tests/conftest.py | AMBIGUOUS |
| <module> | api/clips.py | get | tests/conftest.py | AMBIGUOUS |
| <module> | api/clips.py | delete | tests/conftest.py | AMBIGUOUS |
| <module> | api/health.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_google_id_token | auth/google.py | get | tests/conftest.py | AMBIGUOUS |
| verify_access_token | auth/jwt.py | get | tests/conftest.py | AMBIGUOUS |
| verify_access_token | auth/jwt.py | get | tests/conftest.py | AMBIGUOUS |
| delete | cache/cache_manager.py | delete | tests/conftest.py | EXTRACTED |
| set | cache/cache_manager.py | setex | tests/conftest.py | EXTRACTED |
| get | cache/cache_manager.py | get | tests/conftest.py | EXTRACTED |
| lifespan | app/main.py | disconnect_redis | cache/redis.py | EXTRACTED |
| lifespan | app/main.py | connect_redis | cache/redis.py | EXTRACTED |
| lifespan | app/main.py | create_tables | db/init_db.py | EXTRACTED |
| lifespan | app/main.py | init_db | db/init_db.py | EXTRACTED |


## Potential Dead Code
_Functions with zero callers (not guaranteed dead — may be entry points or called via reflection)._

| Function | File |
| --- | --- |
| do_run_migrations | alembic/env.py |
| downgrade | versions/2287a0526df5_add_uploader.py |
| upgrade | versions/2287a0526df5_add_uploader.py |
| downgrade | versions/8e94b0730971_create_clips_table.py |
| upgrade | versions/8e94b0730971_create_clips_table.py |
| downgrade | versions/dc1fe517afdd_add_users_and_clip_ownership.py |
| upgrade | versions/dc1fe517afdd_add_users_and_clip_ownership.py |
| get_me | api/auth.py |
| login | api/auth.py |
| logout | api/auth.py |
| register | api/auth.py |
| list_boards | api/boards.py |
| get_current_user | api/dependencies.py |
| create_guest_clip | api/guest.py |
| get_or_create_guest_board | api/guest.py |
| health_check | api/health.py |
| get_settings | api/settings.py |
| update_settings | api/settings.py |
| upload_file | api/upload.py |
| verify_google_id_token | auth/google.py |


## Suggested Cypher Queries
_Copy these into `execute_cypher_query` to explore further._

### Callers of a specific function
```cypher
MATCH (caller)-[:CALLS|HEURISTIC_CALLS]->(fn:Function {name: 'yourFunctionName'})
RETURN caller.name, caller.path LIMIT 20
```

### Class hierarchy for a specific class
```cypher
MATCH path = (c:Class {name: 'YourClass'})-[:INHERITS*]->(parent)
RETURN [n IN nodes(path) | n.name] AS hierarchy
```

### Most-injected Spring beans
```cypher
MATCH ()-[:INJECTS]->(bean:Class)
RETURN bean.name, count(*) AS injection_count
ORDER BY injection_count DESC LIMIT 10
```

### All external library dependencies
```cypher
MATCH (m:MavenModule)-[:USES_LIBRARY]->(lib:ExternalLibrary)
RETURN m.artifact_id, lib.group_id, lib.artifact_id, lib.version
ORDER BY lib.artifact_id
```

### CALLS edges with low confidence (potential mis-resolutions)
```cypher
MATCH (a)-[c:CALLS|HEURISTIC_CALLS]->(b)
WHERE c.confidence_label = 'AMBIGUOUS'
RETURN a.name, b.name, c.resolution_tier, a.path LIMIT 20
```
