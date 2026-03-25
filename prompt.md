Master build prompt for Google Antigravity

Build a production-style hackathon prototype of a Bengali-only disaster early-warning voice AI system plus web app for Bangladesh, focused on cyclone, storm surge, flood, flash flood, waterlogging, landslide, and river erosion risk.

The system is for vulnerable edge communities. It must simulate large-scale outbound warning calls, talk with people in Bengali, provide context-aware safety guidance, ask short survey questions, personalize recommendations from a person database, extract structured risk and need data, store results in PostgreSQL, and visualize vulnerable households on a map for government and NGO decision support.

1. Product goal

Create a full-stack application that does all of the following:

Accepts a disaster alert event from an operator dashboard.
Simulates simultaneous outbound phone calls to many people from a provided person database.
For prototype mode, since real telephony is not available, exposes a web endpoint that opens a “call simulation” page:
operator chooses a user/person from the database
presses a call button
a full phone-like Bengali conversation starts in the browser
AI speaks to the user using TTS
user speaks or types back
ASR transcribes speech
LLM drives the conversation
RAG retrieves relevant safety guidance
the app extracts structured data from the conversation
results are stored in PostgreSQL
Provides person-specific recommendations based on the uploaded household/person dataset.
Creates a vulnerability map and priority map showing extracted needs, evacuation barriers, WASH risks, fragile housing, livelihood risk, and follow-up priority.
Is containerized and deployment-ready for Koyeb.
Uses environment variables for all secrets and external service configuration.
Includes Dockerfile, docker-compose or equivalent local dev setup, requirements, migrations, seed scripts, and clear README.
2. Critical operating constraints
All user-facing conversation must be in Bengali.
The AI must use the uploaded guideline documents as the primary source of truth for dialogue style, question flow, escalation logic, risk logic, and extraction schema. The sample script contains greeting, consent, warning-awareness, housing, vulnerability, local condition, water/latrine risk, evacuation, asset-risk, and closing patterns.
The cyclone playbook contains hazard logic, housing guidance, WASH guidance, livelihood guidance, vulnerability guidance, escalation rules, extraction schema, priority logic, and RAG chunking recommendations for cyclone/storm-surge contexts.
The flood playbook contains the same kind of guidance for river flood, flash flood, heavy rainfall, waterlogging, landslide, and river erosion, including timing-based actions, WASH safety, housing-risk logic, vulnerability handling, and extraction fields.
The uploaded spreadsheet contains person records that must be used for personalized suggestions.
OpenAI API must be used for LLM tasks.
Google Text-to-Speech must be used for TTS.
ASR must use ai4bharat/indic-conformer-600m-multilingual locally.
PostgreSQL must be used for persistence.
Prefer Koyeb for deployment, but if a better architecture is justified for reliability or GPU availability, document the alternative and still provide a Koyeb-first deployment path.
3. Core use cases
3.1 Operator use case

An operator can:

create or trigger an alert campaign
choose hazard type
set district/upazila/union scope
define warning severity and lead time
see queued people to call
launch prototype web-call simulation for one selected person
monitor call outcomes
view extracted structured data
view risk map and summary dashboard
3.2 Household/person use case

A household member receives a simulated call page and can:

hear a Bengali warning message
respond in Bengali by voice or text
get concise, respectful, practical safety guidance
answer short questions
receive personalized suggestions based on livelihood, housing type, WASH risk, vulnerability, and location exposure
end the call naturally
3.3 Decision-maker use case

Government or NGO staff can:

see which households are likely most vulnerable
filter by location, housing type, vulnerable members, inability to evacuate, water contamination risk, livelihood risk, and follow-up need
see map layers and summary counts
identify urgent households needing human callback or referral
4. Required deliverables

Build the full repository with at least these components:

4.1 Backend API

Use Python with FastAPI.

Required capabilities:

auth-ready API structure
campaign creation endpoint
event/hazard trigger endpoint
person selection endpoint
simulated call session endpoint
transcript ingestion endpoint
ASR processing endpoint
RAG retrieval endpoint
extraction endpoint
call completion endpoint
dashboard analytics endpoint
map GeoJSON endpoint
health check endpoint
4.2 Frontend web app

Use React + Next.js or Vite React + a modern UI stack.

Required pages:

login-ready shell
operator dashboard
people list / selector
campaign details page
call simulation page
transcript / extraction viewer
analytics dashboard
map page
4.3 Voice simulation experience

The call simulation page must visually mimic a phone call:

call button
ringing state
connected state
Bengali AI voice playback
microphone permission flow
live transcript panel
fallback text input if microphone is unavailable
end call button
post-call summary view
4.4 RAG pipeline

Implement document ingestion for:

Cyclone_RAG_bangla_rimes.docx
Flood_RAG_Bangla.docx
script_rimes.docx

Required pipeline:

parse DOCX
clean text
chunk intelligently
attach metadata
embed chunks
store in vector DB
retrieve context during conversation

Use the uploaded playbooks’ recommended chunk families and metadata concepts:

hazard routing
timeline-based actions
housing guidance
WASH guidance
livelihood guidance
vulnerable-group guidance
survey/extraction schema
escalation rules
4.5 PostgreSQL schema

Create proper normalized models and migrations.

Required tables:

people
locations
campaigns
hazard_events
call_sessions
call_turns
transcripts
extracted_assessments
followups
map_features
rag_documents
rag_chunks
audit_logs
4.6 Extraction + analytics

Implement structured extraction from conversation into PostgreSQL using tool-calling or structured outputs.

Must extract at least:

call_status: completed / partial / failed / callback
warning_awareness: yes / no / unsure
location: district, upazila, union, village, optional GPS
housing_type: jhupri / kacha / semi-pucca / pucca
water_source_risk: tube well protected / unprotected / already contaminated / unknown
latrine_risk: stable / flood-prone / damaged / unknown
livelihood: fisherman / fish farmer / farmer / salt farmer / livestock owner / other
vulnerable_members: elderly / disability / pregnancy / children / chronic illness
can_evacuate: yes / no / with assistance
current_local_condition: no impact / water rising / strong wind / road blocked / embankment issue
asset_at_risk: livestock / nets / boat / seed / crop / documents / other
priority_class: low / medium / high / urgent
recommended_followup: human callback / volunteer referral / shelter info / medical support / none

Also extract these additional fields because they are necessary for damage/usefulness estimation:

estimated_property_damage_risk_bdt
estimated_property_salvageable_bdt
damage_confidence
key_assets_named
evacuation_barrier_reason
medical_urgency
wash_urgency
transcript_summary_bn
agent_notes_internal_en
4.7 Mapping

Create a modern interactive map.

Use a strong framework such as:

Mapbox GL JS, or
Leaflet + vector tiles, or
deck.gl if useful

Map requirements:

cluster markers
household-level detail popup
filter panel
color by priority
layer toggles
heatmap / cluster mode
hazard-specific styling
export visible data as GeoJSON/CSV
search by district/upazila/union/village
support optional GPS if available, otherwise geocode from administrative fields

Required map layers:

vulnerable household layer
evacuation barrier layer
WASH risk layer
fragile housing layer
livelihood exposure layer
urgent callback layer
probable property damage layer
salvage opportunity layer
5. Recommended technical architecture

Use this target architecture unless a better one is strongly justified:

5.1 Backend
FastAPI
SQLAlchemy or SQLModel
Alembic
PostgreSQL
pgvector for embeddings
Celery or Dramatiq for async jobs
Redis for queue and realtime state
Pydantic for schema validation
5.2 Frontend
React
TypeScript
Tailwind CSS
shadcn/ui or equivalent
TanStack Query
Zustand or equivalent simple client state
Mapbox GL or Leaflet
5.3 AI/voice
OpenAI for conversation orchestration, extraction, summarization, and tool calling
Google Cloud Text-to-Speech for Bengali voice synthesis
ai4bharat/indic-conformer-600m-multilingual for Bengali ASR running locally on GPU
a local audio pipeline for upload/transcode/chunking
server-side VAD or turn segmentation if feasible
5.4 Vector / retrieval
pgvector preferred for simplicity, unless Qdrant is clearly better
embed RAG chunks with OpenAI embeddings
metadata-aware retrieval
hazard- and phase-aware retrieval strategy
5.5 Deployment

Target Koyeb:

one web service for frontend/backend
one worker service
one PostgreSQL database
one Redis instance if supported, else external Redis
one GPU instance for ASR inference, preferably RTX-4000-SFF-ADA as requested

If Koyeb GPU limitations are problematic, document a recommended split:

Koyeb for web app + API + Postgres
separate GPU worker host for ASR
but still keep the repo deployable with Koyeb-compatible defaults
6. Conversation design requirements
6.1 Language policy
All live conversation content must be in natural Bengali.
Internal code comments and developer docs can be English.
RAG retrieval may use metadata in English, but generated speech/text to end users must be Bengali.
6.2 Tone
calm
respectful
concise
practical
non-patronizing
no false reassurance
no contradiction of official evacuation orders

This is explicitly aligned with the uploaded cyclone and flood playbooks, which require short, practical, action-oriented guidance, prioritization of life safety, escalation when danger is active, and no contradiction of official orders.

6.3 Conversation stages

Implement the conversation as a state machine:

Greeting and consent
Warning awareness check
Situation framing
Hazard-specific guidance
Household profiling questions
Vulnerability assessment
Current local condition check
WASH risk check
Evacuation ability check
Asset/livelihood risk check
Personalized guidance
Extraction confirmation
Closing and social spreading request

The sample script already provides the basic structure for greeting, awareness, livelihood, house type, vulnerability, local condition, WASH, evacuation, asset risk, and closing.

6.4 Safety logic

The agent must:

switch from survey mode to urgent safety mode if immediate danger is reported
shorten questions if the person is in active danger
prioritize life safety over asset protection
never promise rescue, compensation, or unavailable support
escalate urgent cases into recommended_followup
6.5 Hazard routing

Support at least:

cyclone
storm surge
river flood
flash flood
heavy rainfall
waterlogging
landslide
river erosion
mixed hazard

Cyclone/storm-surge logic should follow the cyclone playbook. Flood/flash flood/heavy rainfall/waterlogging/landslide/erosion logic should follow the flood playbook.

7. Personalization logic

Use the spreadsheet data plus conversation data to personalize guidance.

Possible personalization dimensions:

district/upazila/union/village
livelihood
house type
vulnerable members
water source type/risk
latrine risk
evacuation ability
current local condition
named assets at risk

Examples:

fisherman: emphasize not going back to sea, securing nets/boat safely, early movement
fish farmer: pond/gher protection if safe, but no staying behind in severe risk
farmer: seed/crop/tool protection, early movement if water is rising
salt farmer: field/product protection if time permits
livestock owner: early relocation of animals if possible
elderly/pregnancy/disability/children: earlier evacuation and follow-up priority
jhupri/kacha housing: stronger early shelter messaging
water-source contamination risk: immediate safe water guidance

These patterns are directly reflected in the uploaded playbooks.

8. Property damage and salvage estimation

Implement a pragmatic prototype estimation module.

Goal:
From the person profile and conversation, estimate:

probable property damage
probable property that can still be saved within the remaining lead time

This does not need to be perfect actuarial modeling. Build a transparent heuristic + LLM-assisted estimator.

Inputs may include:

hazard type
severity
lead time
house type
current condition
livelihood
assets at risk
vulnerability and evacuation barriers
whether warnings were known earlier
whether the household has started moving assets

Outputs:

estimated total assets at risk
estimated probable damage amount in BDT
estimated salvageable amount in BDT
confidence score
reasoning summary
top risk drivers
top salvage actions still possible

Store these in DB and expose them in the dashboard and map.

9. Database design details

Design the schema so every call session can be replayed and audited.

Suggested core entities:

people
id
external_person_id
name
phone
gender_optional
district
upazila
union_name
village
lat
lng
housing_type_known
livelihood_known
vulnerable_members_known
notes
hazard_events
id
event_type
title
severity
official_signal
lead_time_hours
source
district_scope
upazila_scope
metadata_json
created_at
campaigns
id
hazard_event_id
status
total_targets
started_at
completed_at
call_sessions
id
campaign_id
person_id
mode
status
started_at
ended_at
transcript_text
transcript_summary_bn
raw_asr_json
extraction_json
llm_trace_json
extracted_assessments
id
call_session_id
all required structured fields
probable_damage_bdt
salvageable_bdt
support_priority_score
created_at
followups
id
call_session_id
followup_type
reason
status
assigned_to
created_at
map_features
id
person_id
call_session_id
geom
priority_class
layer_flags_json
popup_summary_bn
updated_at
10. RAG implementation requirements

Implement robust RAG instead of dumping full documents into prompts.

10.1 Document ingestion

For each uploaded DOCX:

parse all paragraphs and tables
preserve headings
infer section boundaries
normalize whitespace
store source doc name
10.2 Chunking

Use semantic chunking with overlap.
Try chunk sizes around 250–500 words.
Preserve metadata such as:

hazard_type
lead_time_band
signal_band
housing_type
livelihood
wash_asset
vulnerability_group
phase = before/during/after
action_priority = life_safety/health/asset/survey/escalation
geography relevance if present

This mirrors the chunking recommendations in the uploaded playbooks.

10.3 Retrieval strategy

At every turn, retrieve by:

hazard type
current conversation stage
household profile
vulnerability
location exposure
timing/lead time
whether urgent escalation is needed
10.4 Grounding strategy

Use retrieved guidance to produce:

short Bengali instructions
no hallucinated shelter locations unless actual shelter data exists
no contradiction of official instructions
no excessive verbosity
11. ASR/TTS/audio pipeline
11.1 ASR

Use ai4bharat/indic-conformer-600m-multilingual locally.
Requirements:

speech upload endpoint
streaming or chunked inference if feasible
Bengali transcript output
confidence or segment metadata if available
handle browser microphone audio conversion
11.2 TTS

Use Google Cloud Text-to-Speech.
Requirements:

Bengali voice output
cache repeated prompt fragments if possible
low-latency synthesis pipeline
return audio URL or stream
11.3 Audio UX
browser records user voice
sends to backend
backend transcribes
LLM responds
TTS synthesizes reply
frontend plays audio
transcript panel updates live
12. Operator dashboard requirements

Must show:

active campaigns
people queued / completed / failed
call status counts
warning awareness rate
evacuation ability distribution
priority distribution
households with vulnerable members
WASH-risk households
likely damaged property total
likely salvageable property total
urgent follow-up list

Provide filters by:

hazard type
district
upazila
union
housing type
livelihood
priority class
follow-up type
13. Map requirements in more detail

Each marker popup should show:

person name or anonymized ID
location
livelihood
housing type
vulnerable members
can evacuate
current local condition
priority
follow-up recommendation
probable damage
salvageable amount
last call timestamp
summary in Bengali

Use color rules:

low = green
medium = yellow
high = orange
urgent = red

Add derived thematic layers:

unsafe water hotspot
severe fragile housing cluster
marine livelihood exposure cluster
flood-affected households
women/children/elderly vulnerability concentration
medical follow-up need
evacuation assistance need
14. Admin + data import requirements

Provide:

script to import the uploaded spreadsheet into PostgreSQL
location normalization
duplicate handling
validation reports
seed script for demo data
admin endpoint or CLI command to re-run imports
15. Prompting and agent orchestration design

Implement the AI logic with separate internal modules/prompts:

conversation_orchestrator
rag_retriever
risk_extractor
damage_estimator
followup_classifier
map_summary_generator

Use tool-calling or structured schema output for extraction.
Make the orchestrator maintain:

conversation stage
language = Bengali
urgency level
retrieved guidance snippets
known household profile
missing fields
16. Non-functional requirements
clean architecture
typed code where possible
modular services
useful logs
error handling
retries for external APIs
async background jobs for non-blocking processing
secure secret handling
no hardcoded secrets
responsive UI
deployable with Docker
easy local setup
17. Files that must exist in repo

At minimum create:

README.md
.env.example
Dockerfile
docker-compose.yml or local equivalent
requirements.txt or pyproject.toml
frontend/package.json
backend/
frontend/
alembic/
scripts/import_people.py
scripts/ingest_rag_docs.py
scripts/seed_demo.py
scripts/run_local_gpu_asr.py
docs/architecture.md
docs/data_model.md
docs/deployment_koyeb.md
docs/prompting_strategy.md
instruction.md
18. Environment variables

Create .env.example with placeholders for all required values, including:

OPENAI_API_KEY=
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_TTS_PROJECT_ID=
DATABASE_URL=
REDIS_URL=
MAPBOX_TOKEN= or map provider key if used
ASR_MODEL_NAME=ai4bharat/indic-conformer-600m-multilingual
ASR_DEVICE=cuda
ASR_BATCH_SIZE=
PGVECTOR_ENABLED=true
APP_BASE_URL=
SECRET_KEY=
CORS_ORIGINS=
ENVIRONMENT=development

If any secret is not strictly required for first boot, still include placeholder variables.

19. Demo / prototype behavior

Since direct phone calling is unavailable, expose a browser route like:

/simulate-call?person_id=<id>&event_id=<id>

Behavior:

opens a call UI
greets in Bengali
plays disaster warning
asks user questions
retrieves guidance from RAG
personalizes advice using person profile
extracts structured fields
stores everything in DB
shows final Bengali summary

Also create a batch simulation mode for demo:

operator triggers event
system creates many simulated queued calls
UI shows progress and call outcomes
optionally use mock responders for auto-demo data generation
20. Acceptance criteria

The build is successful only if all of the following work:

App boots with Docker locally.
Spreadsheet imports successfully into PostgreSQL.
RAG docs ingest successfully and are queryable.
Simulated call page works in Bengali.
Voice input or text fallback works.
TTS audio plays back.
Structured fields are extracted and saved.
Property damage and salvage estimates are generated.
Dashboard shows campaign analytics.
Map shows priority-coded households.
Repo includes deploy instructions for Koyeb.
.env.example is complete.
Code is modular and understandable.
README explains local run, deployment, ingestion, and demo flow.
21. Important product rules
Never contradict official warning/evacuation instructions.
Never fabricate shelter locations unless actual shelter data exists.
Use short actionable messages, usually 3–5 key actions.
In active danger, stop asking unnecessary questions and prioritize life-safety messaging.
Bengali must remain the only end-user conversational language.
Personalization should improve action quality without becoming intrusive.
Extraction should be schema-first and auditable.
Be honest in estimation outputs: use “probable” and “estimated,” not false certainty.
22. Use the uploaded docs as source-of-truth content

Treat these uploaded files as canonical guidance sources:

script_rimes.docx for sample conversational structure and Bengali phrasing
Cyclone_RAG_bangla_rimes.docx for cyclone/storm-surge conversation logic, guidance retrieval, extraction schema, escalation rules, and chunking metadata
Flood_RAG_Bangla.docx for flood/flash flood/heavy rain/waterlogging/landslide/erosion logic, WASH guidance, vulnerability logic, extraction schema, and chunking metadata
Pseudo_Human_Database_Hackathon.xlsx for person-level personalization data
23. Output format I want from you

When building, do not just explain. Create the actual project.

I want:

full codebase
migrations
ingestion scripts
runnable frontend and backend
Docker setup
.env.example
deployment docs
internal instruction.md
sample seeded demo data
polished UI for demo presentation

Start by generating the full repository structure and implementation.